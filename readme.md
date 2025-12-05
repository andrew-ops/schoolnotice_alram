# 🔔 호서대학교 공지사항 알림 서비스

호서대학교의 다양한 공지사항을 한 눈에 확인할 수 있는 웹 서비스입니다.

## ✨ 주요 기능

- 📚 **9개 사이트** 공지사항 통합 크롤링
- 🏷️ [태그] 기반 필터링 기능
- 🔍 초성 검색 지원 (ㄱㅈㅅ → 공지사항)
- 🔄 백그라운드 자동 업데이트 (50분 주기)
- 💾 JSON 캐시로 빠른 서빙
- 🎯 캔두 프로그램 마감/진행중 상태 표시

---

## 📡 크롤링 사이트 목록

| 구분 | 사이트명 | URL | 설명 |
|:---:|:---:|:---|:---|
| 📚 | **도서관** | `library.hoseo.ac.kr` | 도서관 공지사항 |
| 🏫 | **메인공지** | `hoseo.ac.kr` (전체) | 학교 메인 공지사항 |
| 🔬 | **융합교육** | `hoseo.ac.kr` (융합교육) | 융합교육원 공지 |
| 📝 | **학사** | `hoseo.ac.kr` (학사) | 학사 관련 공지 |
| 💰 | **장학** | `hoseo.ac.kr` (장학) | 장학금 관련 공지 |
| 🤝 | **사회봉사** | `hoseo.ac.kr` (사회봉사) | 봉사활동 관련 공지 |
| 📢 | **외부공지** | `hoseo.ac.kr` (외부) | 외부기관 공지 |
| 💼 | **취업** | `hoseo.ac.kr` (취업) | 취업 관련 공지 |
| 🎯 | **캔두** | `cando.hoseo.ac.kr` | 비교과 프로그램 (1~2페이지) |

---

## 📁 프로젝트 구조

```
schoolnotice_alram/
├── backend/
│   ├── app.py              # Flask 서버 & 캐시 관리
│   ├── scraper.py          # Selenium 크롤링 로직
│   ├── cache.json          # 캐시 데이터
│   ├── requirements.txt    # Python 패키지
│   └── candocookie.env     # 캔두 인증 쿠키
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js          # React 메인 컴포넌트
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
└── README.md
```

---

## 🚀 설치 및 실행

### 1. 백엔드 (Flask)

```bash
cd backend

# 가상환경 생성 (권장)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 패키지 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

> 서버: http://localhost:5000

### 2. 프론트엔드 (React)

```bash
cd frontend

# 패키지 설치
npm install

# 개발 서버 실행
npm start
```

> 브라우저: http://localhost:3000

---

## 📡 API 엔드포인트

| Method | 엔드포인트 | 설명 |
|:---:|:---|:---|
| GET | `/api/all` | 전체 공지사항 (통합) |
| GET | `/api/sources` | 소스 목록 조회 |
| GET | `/api/status` | 캐시 상태 확인 |
| POST | `/api/refresh` | 캐시 강제 갱신 |
| GET | `/api/health` | 서버 상태 확인 |

---

## 🛠️ 기술 스택

| 구분 | 기술 |
|:---:|:---|
| **Backend** | Python, Flask, Selenium |
| **Frontend** | React, Axios, es-hangul |
| **Crawling** | Selenium WebDriver (Chrome) |
| **Cache** | JSON 파일 기반 캐싱 |

---

## ⚙️ 캔두 쿠키 설정

캔두 사이트는 로그인이 필요합니다. `backend/candocookie.env` 파일에 쿠키를 설정하세요.

```
cookie=ASP.NET_SessionId=xxx; SCSSO=xxx; USERID=xxx; ...
```

> 브라우저 개발자 도구(F12) → Application → Cookies에서 복사
