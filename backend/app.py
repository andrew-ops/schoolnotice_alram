from flask import Flask, jsonify
from flask_cors import CORS
from scraper import NoticeScraper
import re
import threading
import time
from datetime import datetime
import atexit
import json
import os

app = Flask(__name__)
CORS(app)

# ===== 설정 =====
CACHE_FILE_PATH = os.path.join(os.path.dirname(__file__), 'cache.json')
CACHE_UPDATE_INTERVAL = 3000  # 50분마다 백그라운드 크롤링
MAIN_PAGE_START = 2  # 2페이지부터 (1페이지는 상단공지)
MAIN_PAGE_END = 5

# ===== 소스 정의 =====
SOURCES = {
    "library": {
        "name": "도서관",
        "color": "#43a047",
        "icon": "📚"
    },
    "main": {
        "name": "메인공지",
        "color": "#1a73e8",
        "icon": "🏫"
    },
    "fusion": {
        "name": "융합교육",
        "color": "#9c27b0",
        "icon": "🔬"
    },
    "academic": {
        "name": "학사",
        "color": "#f44336",
        "icon": "📝"
    },
    "scholarship": {
        "name": "장학",
        "color": "#ff9800",
        "icon": "💰"
    },
    "volunteer": {
        "name": "사회봉사",
        "color": "#4caf50",
        "icon": "🤝"
    },
    "external": {
        "name": "외부공지",
        "color": "#607d8b",
        "icon": "📢"
    },
    "career": {
        "name": "취업",
        "color": "#2196f3",
        "icon": "💼"
    },
    "cando": {
        "name": "캔두",
        "color": "#e91e63",
        "icon": "🎯"
    }
}

# ===== 캐시 및 상태 관리 =====
cache = {source: {"data": [], "tags": [], "last_updated": None} for source in SOURCES}

cache_lock = threading.Lock()
scraper_lock = threading.Lock()
scraper = None
background_thread = None
is_running = True

def load_cache_from_file():
    """JSON 파일에서 캐시 로드"""
    global cache
    try:
        if os.path.exists(CACHE_FILE_PATH):
            with open(CACHE_FILE_PATH, 'r', encoding='utf-8') as f:
                loaded_cache = json.load(f)
                with cache_lock:
                    for source_key in SOURCES:
                        if source_key in loaded_cache:
                            cache[source_key] = loaded_cache[source_key]
                print(f"[{datetime.now()}] 캐시 파일 로드 완료: {CACHE_FILE_PATH}")
                return True
    except Exception as e:
        print(f"[WARNING] 캐시 파일 로드 실패: {e}")
    return False

def save_cache_to_file():
    """캐시를 JSON 파일로 저장"""
    try:
        with cache_lock:
            cache_copy = {k: v.copy() for k, v in cache.items()}
        
        with open(CACHE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cache_copy, f, ensure_ascii=False, indent=2)
        print(f"[{datetime.now()}] 캐시 파일 저장 완료: {CACHE_FILE_PATH}")
        return True
    except Exception as e:
        print(f"[ERROR] 캐시 파일 저장 실패: {e}")
        return False

def get_scraper():
    global scraper
    with scraper_lock:
        if scraper is None:
            scraper = NoticeScraper()
        return scraper

def reset_scraper():
    """드라이버 세션 문제 시 스크래퍼 재생성"""
    global scraper
    with scraper_lock:
        if scraper is not None:
            try:
                scraper.close()
            except:
                pass
            scraper = None
        scraper = NoticeScraper()
        return scraper

def close_scraper():
    global scraper
    with scraper_lock:
        if scraper is not None:
            try:
                scraper.close()
            except:
                pass
            scraper = None

def extract_tags(title):
    """제목에서 [xxxx] 형태의 태그 추출"""
    tags = re.findall(r'\[([^\]]+)\]', title)
    return tags

def process_notices(notices, source):
    """공지사항 데이터에 태그 정보 추가"""
    processed = []
    for i in range(len(notices["제목"])):
        title = notices["제목"][i]
        link = notices["링크"][i]
        tags = extract_tags(title)
        
        notice_data = {
            "id": f"{source}-{i + 1}",
            "title": title,
            "link": link,
            "date": notices["날짜"][i],
            "tags": tags,
            "source": source,
            "sourceName": SOURCES[source]["name"],
            "sourceColor": SOURCES[source]["color"],
            "sourceIcon": SOURCES[source]["icon"]
        }
        
        # 캔두의 경우 상태 정보 추가
        if "상태" in notices and i < len(notices["상태"]):
            notice_data["status"] = notices["상태"][i]
        
        processed.append(notice_data)
    return processed

def merge_notices(existing_data, new_data, source_key=None):
    """기존 데이터와 새 데이터를 병합 (중복 제거, 새 공지 추가)"""
    # 기존 데이터를 (title, link) 기준으로 딕셔너리화
    existing_map = {}
    for notice in existing_data:
        key = (notice.get("title", ""), notice.get("link", ""))
        existing_map[key] = notice
    
    # 새 데이터 병합 (새 공지 추가, 기존 공지 업데이트)
    new_count = 0
    updated_count = 0
    status_changed_count = 0
    
    for notice in new_data:
        key = (notice.get("title", ""), notice.get("link", ""))
        if key not in existing_map:
            # 새로운 공지 추가
            existing_map[key] = notice
            new_count += 1
        else:
            # 캔두의 경우 상태 변화 감지
            if source_key == "cando":
                old_status = existing_map[key].get("status", "")
                new_status = notice.get("status", "")
                if old_status != new_status:
                    status_changed_count += 1
                    print(f"[STATUS] '{notice.get('title', '')[:30]}...' 상태 변경: {old_status} → {new_status}")
            
            # 기존 공지 업데이트
            existing_map[key].update(notice)
            updated_count += 1
    
    # 결과를 리스트로 변환
    merged_list = list(existing_map.values())
    
    return merged_list, new_count, updated_count, status_changed_count

def crawl_source(source_key):
    """특정 소스 크롤링"""
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            s = get_scraper()
            
            if source_key == "library":
                notices = s.library()
            elif source_key == "main":
                notices = s.main_pg(page_start=MAIN_PAGE_START, page_end=MAIN_PAGE_END)
            elif source_key == "fusion":
                notices = s.main_fusion()
            elif source_key == "academic":
                notices = s.main_academic()
            elif source_key == "scholarship":
                notices = s.main_scholarship()
            elif source_key == "volunteer":
                notices = s.main_volunteer()
            elif source_key == "external":
                notices = s.main_external()
            elif source_key == "career":
                notices = s.main_career()
            elif source_key == "cando":
                notices = s.cando()
            else:
                return None, None
            
            processed = process_notices(notices, source_key)
            
            all_tags = set()
            for notice in processed:
                all_tags.update(notice["tags"])
            
            return processed, list(all_tags)
        except Exception as e:
            error_msg = str(e).lower()
            print(f"[ERROR] {source_key} 크롤링 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            
            # 세션 관련 오류면 드라이버 재생성
            if "invalid session" in error_msg or "session" in error_msg or "disconnected" in error_msg:
                print(f"[INFO] 세션 오류 감지, 드라이버 재생성...")
                reset_scraper()
            
            if attempt == max_retries - 1:
                return None, None
    
    return None, None

def update_cache():
    """전체 캐시 업데이트 (기존 데이터 유지, 새 데이터 병합)"""
    global cache
    
    print(f"[{datetime.now()}] 캐시 업데이트 시작...")
    
    consecutive_failures = 0
    max_failures = 3
    updated_count = 0
    total_new = 0
    total_status_changed = 0
    
    for source_key in SOURCES:
        try:
            data, tags = crawl_source(source_key)
            if data is not None:
                with cache_lock:
                    # 기존 데이터와 병합
                    existing_data = cache[source_key]["data"]
                    merged_data, new_count, upd_count, status_changed = merge_notices(existing_data, data, source_key)
                    
                    # ID 재할당 (병합 후 순서 정리)
                    for i, notice in enumerate(merged_data):
                        notice["id"] = f"{source_key}-{i + 1}"
                    
                    # 태그 병합
                    existing_tags = set(cache[source_key]["tags"])
                    existing_tags.update(tags)
                    
                    cache[source_key]["data"] = merged_data
                    cache[source_key]["tags"] = list(existing_tags)
                    cache[source_key]["last_updated"] = datetime.now().isoformat()
                
                # 로그 출력
                log_msg = f"[{datetime.now()}] {SOURCES[source_key]['name']} 캐시 업데이트: 총 {len(merged_data)}건 (신규 {new_count}건"
                if source_key == "cando" and status_changed > 0:
                    log_msg += f", 상태변경 {status_changed}건"
                log_msg += ")"
                print(log_msg)
                
                consecutive_failures = 0
                updated_count += 1
                total_new += new_count
                total_status_changed += status_changed
            else:
                consecutive_failures += 1
        except Exception as e:
            print(f"[ERROR] {source_key} 업데이트 실패: {e}")
            consecutive_failures += 1
        
        # 연속 실패 시 드라이버 재생성
        if consecutive_failures >= max_failures:
            print(f"[WARNING] 연속 {max_failures}회 실패, 드라이버 재생성 중...")
            reset_scraper()
            consecutive_failures = 0
    
    # 캐시를 JSON 파일로 저장
    if updated_count > 0:
        save_cache_to_file()
    
    # 최종 로그
    final_log = f"[{datetime.now()}] 캐시 업데이트 완료! ({updated_count}/{len(SOURCES)} 소스, 신규 {total_new}건"
    if total_status_changed > 0:
        final_log += f", 상태변경 {total_status_changed}건"
    final_log += ")"
    print(final_log)

def background_crawler():
    """백그라운드에서 주기적으로 크롤링"""
    global is_running
    
    time.sleep(2)
    update_cache()
    
    while is_running:
        time.sleep(CACHE_UPDATE_INTERVAL)
        if is_running:
            update_cache()

def start_background_crawler():
    """백그라운드 크롤러 시작"""
    global background_thread
    
    # 먼저 캐시 파일에서 로드 시도
    cache_loaded = load_cache_from_file()
    
    background_thread = threading.Thread(target=background_crawler, daemon=True)
    background_thread.start()
    
    if cache_loaded:
        print(f"[{datetime.now()}] 기존 캐시 로드됨, 백그라운드에서 업데이트 진행")
    print(f"[{datetime.now()}] 백그라운드 크롤러 시작됨 (업데이트 주기: {CACHE_UPDATE_INTERVAL}초)")

def shutdown_handler():
    """종료 시 정리"""
    global is_running
    is_running = False
    save_cache_to_file()  # 종료 전 캐시 저장
    close_scraper()
    print("서버 종료 처리 완료")

atexit.register(shutdown_handler)

# ===== API 엔드포인트 =====

@app.route('/api/sources', methods=['GET'])
def get_sources():
    """소스 목록 API"""
    return jsonify({
        "success": True,
        "sources": SOURCES
    })

@app.route('/api/all', methods=['GET'])
def get_all_notices():
    """전체 공지사항 통합 API"""
    all_notices = []
    all_tags = set()
    source_counts = {}
    
    with cache_lock:
        for source_key in SOURCES:
            source_data = cache[source_key]["data"]
            source_tags = cache[source_key]["tags"]
            
            all_notices.extend(source_data)
            all_tags.update(source_tags)
            source_counts[source_key] = len(source_data)
    
    # 날짜 기준 정렬 (최신순)
    def parse_date(notice):
        date_str = notice.get("date", "")
        try:
            # YYYY.MM.DD 또는 YYYY-MM-DD 형식
            clean_date = date_str.replace(".", "-").replace("/", "-")
            return clean_date
        except:
            return "0000-00-00"
    
    all_notices.sort(key=parse_date, reverse=True)
    
    return jsonify({
        "success": True,
        "notices": all_notices,
        "tags": list(all_tags),
        "sources": SOURCES,
        "sourceCounts": source_counts,
        "cached": True
    })

@app.route('/api/refresh', methods=['POST'])
def force_refresh():
    """강제 캐시 갱신 API"""
    try:
        update_cache()
        return jsonify({
            "success": True,
            "message": "캐시 갱신 완료"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """서버 상태 및 캐시 정보"""
    with cache_lock:
        cache_info = {}
        for source_key in SOURCES:
            cache_info[source_key] = {
                "name": SOURCES[source_key]["name"],
                "count": len(cache[source_key]["data"]),
                "last_updated": cache[source_key]["last_updated"]
            }
        
        # 캐시 파일 정보
        cache_file_exists = os.path.exists(CACHE_FILE_PATH)
        cache_file_size = os.path.getsize(CACHE_FILE_PATH) if cache_file_exists else 0
        cache_file_modified = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE_PATH)).isoformat() if cache_file_exists else None
        
        return jsonify({
            "status": "ok",
            "cache": cache_info,
            "cacheFile": {
                "path": CACHE_FILE_PATH,
                "exists": cache_file_exists,
                "size": cache_file_size,
                "lastModified": cache_file_modified
            },
            "settings": {
                "update_interval_seconds": CACHE_UPDATE_INTERVAL
            }
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    start_background_crawler()
    app.run(debug=False, port=5000, threaded=True)
