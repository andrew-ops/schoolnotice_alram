from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import os

# 캔두 쿠키 로드
def load_cando_cookies():
    """candocookie.env 파일에서 쿠키 로드"""
    cookie_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'candocookie.env')
    cookies = []
    
    try:
        with open(cookie_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # cookie= 부분 파싱
            if content.startswith('cookie='):
                cookie_str = content.replace('cookie=', '').strip()
                # 쿠키 문자열 파싱
                for cookie_pair in cookie_str.split('; '):
                    if '=' in cookie_pair:
                        name, value = cookie_pair.split('=', 1)
                        if name and value:  # 빈 값 제외
                            cookies.append({
                                'name': name.strip(),
                                'value': value.strip(),
                                'domain': 'cando.hoseo.ac.kr'
                            })
    except Exception as e:
        print(f"[WARNING] 쿠키 로드 실패: {e}")
    
    return cookies

class NoticeScraper:
    def __init__(self):
        self.driver = None
        self._setup_driver()

    def _setup_driver(self):
        """드라이버 초기화"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-features=GCMDriver")
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--remote-debugging-port=0")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.page_load_strategy = 'normal'
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(5)
    
    def _ensure_driver(self):
        """드라이버 세션이 유효한지 확인하고 필요시 재생성"""
        try:
            # 세션 유효성 검사
            _ = self.driver.current_url
        except Exception:
            print("[INFO] 드라이버 세션 만료, 재생성 중...")
            self._setup_driver()

    def library(self):
        """도서관 공지사항 크롤링"""
        self._ensure_driver()
        self.driver.get("https://library.hoseo.ac.kr/#/bbs/notice?offset=0&max=200")
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ikc-item")))
        
        title_elements = self.driver.find_elements(By.CLASS_NAME, "ikc-item-title")
        titles = [elem.text for elem in title_elements]
        links = [elem.get_attribute("href") for elem in title_elements]
        
        rows = self.driver.find_elements(By.CLASS_NAME, "ikc-item")
        dates = []
        for row in rows:
            try:
                date_spans = row.find_elements(By.TAG_NAME, "span")
                for span in date_spans:
                    text = span.text
                    if re.match(r'\d{4}\.\d{2}\.\d{2}', text):
                        dates.append(text)
                        break
                else:
                    dates.append("날짜 없음")
            except:
                dates.append("날짜 없음")
        
        return {
            "제목": titles,
            "링크": links,
            "날짜": dates
        }

    def main_category(self, category_code, page_start=1, page_end=5):
        """호서대 홈페이지 카테고리별 공지사항 크롤링"""
        self._ensure_driver()
        all_elements = {
            "제목": [],
            "링크": [],
            "날짜": []
        }
        
        base_url = "https://www.hoseo.ac.kr/Home//BBSView.mbz?action=MAPP_1708240139&schIdx="
        
        for page in range(page_start, page_end + 1):
            try:
                # 매 페이지마다 드라이버 세션 확인
                self._ensure_driver()
                
                url = f"https://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=0&schCategorycode={category_code}&schKeytype=subject&schKeyword=&pageIndex={page}"
                self.driver.get(url)
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.ui-list tbody tr")))
                
                rows = self.driver.find_elements(By.CSS_SELECTOR, "table.ui-list tbody tr")
                
                for row in rows:
                    try:
                        title_td = row.find_element(By.CSS_SELECTOR, "td.board-list-title")
                        title_link = title_td.find_element(By.TAG_NAME, "a")
                        title = title_link.text.strip()
                        
                        onclick_attr = title_link.get_attribute("href")
                        match = re.search(r"fn_viewData\('(\d+)'\)", onclick_attr)
                        if match:
                            article_id = match.group(1)
                            link = base_url + article_id
                        else:
                            link = "링크 없음"
                        
                        date_td = row.find_element(By.CSS_SELECTOR, "td[data-header='등록일자']")
                        date = date_td.text.strip()
                        
                        all_elements["제목"].append(title)
                        all_elements["링크"].append(link)
                        all_elements["날짜"].append(date)
                    except Exception as e:
                        continue
            except Exception as e:
                print(f"[ERROR] 페이지 {page} 크롤링 실패: {e}")
                continue
        
        return all_elements

    def main_pg(self, page_start=1, page_end=5):
        """호서대 홈페이지 공지사항 (전체) 크롤링"""
        return self.main_category("CTG_17082400011", page_start, page_end)
    
    def main_fusion(self, page_start=1, page_end=3):
        """융합교육 공지사항 크롤링"""
        return self.main_category("CTG_24050300117", page_start, page_end)
    
    def main_academic(self, page_start=1, page_end=3):
        """학사 공지사항 크롤링"""
        return self.main_category("CTG_17082400012", page_start, page_end)
    
    def main_scholarship(self, page_start=1, page_end=3):
        """장학 공지사항 크롤링"""
        return self.main_category("CTG_17082400013", page_start, page_end)
    
    def main_volunteer(self, page_start=1, page_end=3):
        """사회봉사 공지사항 크롤링"""
        return self.main_category("CTG_17082400014", page_start, page_end)
    
    def main_external(self, page_start=1, page_end=3):
        """외부 공지사항 크롤링"""
        return self.main_category("CTG_20012200070", page_start, page_end)
    
    def main_career(self, page_start=1, page_end=3):
        """취업 공지사항 크롤링"""
        return self.main_category("CTG_20120400086", page_start, page_end)

    def cando(self, page_start=1, page_end=2):
        """캔두 비교과프로그램 공지사항 크롤링 (쿠키 인증 포함)"""
        self._ensure_driver()
        all_elements = {
            "제목": [],
            "링크": [],
            "날짜": [],
            "상태": []
        }
        
        try:
            # 먼저 도메인 접속 (쿠키 설정 전 필요)
            self.driver.get("https://cando.hoseo.ac.kr")
            
            # 쿠키 설정
            cookies = load_cando_cookies()
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    pass  # 일부 쿠키 실패는 무시
            
            import time
            
            for page in range(page_start, page_end + 1):
                try:
                    # 쿠키 적용 후 프로그램 리스트 페이지 접속
                    self.driver.get(f"https://cando.hoseo.ac.kr/Career/CareerTask/ProgramList.aspx?rp={page}")
                    wait = WebDriverWait(self.driver, 15)
                
                    # prod-list 요소 대기
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".prod-list")))
                    
                    time.sleep(2)  # 추가 대기
                    
                    # prod-list 카드 형태로 크롤링
                    program_cards = self.driver.find_elements(By.CSS_SELECTOR, ".prod-list")
                    print(f"[INFO] 캔두 페이지 {page}: {len(program_cards)}건 발견")
                    
                    for card in program_cards:
                        try:
                            # 제목: prod1 text-info 클래스
                            title_elem = card.find_element(By.CSS_SELECTOR, ".prod1.text-info, [id$='_Title_txt']")
                            title = title_elem.text.strip()
                            
                            # 링크: 카드 내 a 태그 또는 onclick
                            link = "https://cando.hoseo.ac.kr/Career/CareerTask/ProgramList.aspx"
                            try:
                                link_elem = card.find_element(By.TAG_NAME, "a")
                                href = link_elem.get_attribute("href")
                                if href and href != "#":
                                    link = href
                            except:
                                pass
                            
                            # 날짜: DateTime_txt 클래스에서 신청 기간 추출
                            date = "날짜 없음"
                            try:
                                date_elem = card.find_element(By.CSS_SELECTOR, "[id$='_DateTime_txt'], .prod2")
                                date_text = date_elem.text.strip()
                                # "신청2025-12-01~2025-12-31" 형태에서 날짜 추출
                                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                                if date_match:
                                    date = date_match.group(1)
                            except:
                                pass
                            
                            # 상태: 마감 또는 진행중
                            status = "진행중"
                            try:
                                # finishDate 또는 label-white 클래스에서 상태 추출
                                status_elem = card.find_element(By.CSS_SELECTOR, "[name='finishDate'], [id$='_finishDate'], .label.label-white span")
                                status_text = status_elem.text.strip()
                                if "마감" in status_text:
                                    status = "마감"
                                elif status_text:
                                    status = status_text
                            except:
                                # 다른 방법으로 시도
                                try:
                                    labels = card.find_elements(By.CSS_SELECTOR, ".label")
                                    for label in labels:
                                        label_text = label.text.strip()
                                        if "마감" in label_text:
                                            status = "마감"
                                            break
                                        elif "진행" in label_text:
                                            status = "진행중"
                                            break
                                except:
                                    pass
                            
                            if title and len(title) > 1:
                                all_elements["제목"].append(title)
                                all_elements["링크"].append(link)
                                all_elements["날짜"].append(date)
                                all_elements["상태"].append(status)
                                
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    print(f"[ERROR] 캔두 페이지 {page} 크롤링 실패: {e}")
                    continue
                        
        except Exception as e:
            print(f"[ERROR] 캔두 크롤링 실패: {e}")
        
        return all_elements

    def close(self):
        """드라이버 종료"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def __del__(self):
        """소멸자 - 명시적으로 close 호출 필요, 여기서는 안전하게 처리"""
        try:
            self.close()
        except:
            pass
