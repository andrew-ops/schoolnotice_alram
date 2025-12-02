# 호서대학교 공지사항 알림 서비스

호서대학교 도서관과 메인 홈페이지의 공지사항을 한 눈에 확인할 수 있는 웹 서비스입니다.

## 기능

- 📚 도서관 공지사항 크롤링
- 🏫 메인 홈페이지 공지사항 크롤링
- 🏷️ [태그] 기반 필터링 기능
- 🔄 실시간 새로고침

## 프로젝트 구조

```
schoolnotice_alram/
├── backend/
│   ├── app.py          # Flask 서버
│   ├── scraper.py      # 크롤링 로직
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js      # 메인 React 컴포넌트
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
└── main.py             # CLI 버전 (레거시)
```

## 설치 및 실행

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

서버가 http://localhost:5000 에서 실행됩니다.

### 2. 프론트엔드 (React)

```bash
cd frontend

# 패키지 설치
npm install

# 개발 서버 실행
npm start
```

브라우저에서 http://localhost:3000 으로 접속합니다.

## API 엔드포인트

| 엔드포인트 | 설명 |
|------------|------|
| `GET /api/library` | 도서관 공지사항 |
| `GET /api/main` | 메인 홈페이지 공지사항 |
| `GET /api/all` | 전체 공지사항 (도서관 + 메인) |
| `GET /api/health` | 서버 상태 확인 |

## 기술 스택

- **Backend**: Python, Flask, Selenium
- **Frontend**: React, Axios
- **Crawling**: Selenium WebDriver



## 추가해야할 사이트 리스트
```
https://cando.hoseo.ac.kr/Career/CareerTask/ProgramList.aspx -- 캔두
https://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=66216&schCategorycode=CTG_24050300117&schKeytype=subject&schKeyword=&pageIndex=2 -- 메인-융합교육
https://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=66216&schCategorycode=CTG_17082400012&schKeytype=subject&schKeyword=&pageIndex=2 -- 메인--학사
https://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=66216&schCategorycode=CTG_17082400013&schKeytype=subject&schKeyword=&pageIndex=2 -- 메인-장학
https://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=66216&schCategorycode=CTG_17082400014&schKeytype=subject&schKeyword=&pageIndex=2 -- 메인-사회봉사
https://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=66216&schCategorycode=CTG_20012200070&schKeytype=subject&schKeyword=&pageIndex=2 -- 메인-외부
https://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=66216&schCategorycode=CTG_20120400086&schKeytype=subject&schKeyword=&pageIndex=2 -- 메인-취업
https://cando.hoseo.ac.kr/Career/CareerTask/ProgramList.aspx?rp=1 or rp2 -- 캔두


