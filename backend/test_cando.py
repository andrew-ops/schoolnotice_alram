from scraper import NoticeScraper, load_cando_cookies
import time

s = NoticeScraper()

# 먼저 도메인 접속
s.driver.get('https://cando.hoseo.ac.kr')
time.sleep(1)

# 쿠키 로드 및 추가
cookies = load_cando_cookies()
print(f'쿠키 개수: {len(cookies)}')

for c in cookies:
    try:
        s.driver.add_cookie(c)
        print(f'쿠키 추가 성공: {c["name"]}')
    except Exception as e:
        print(f'쿠키 추가 실패: {c["name"]} - {e}')

# 페이지 이동
s.driver.get('https://cando.hoseo.ac.kr/Career/CareerTask/ProgramList.aspx')
time.sleep(3)

print('\n=== 페이지 정보 ===')
print('현재 URL:', s.driver.current_url)
print('페이지 제목:', s.driver.title)

# HTML 저장
with open('cando_page.html', 'w', encoding='utf-8') as f:
    f.write(s.driver.page_source)
print('\nHTML 저장 완료: cando_page.html')

# 주요 요소 탐색
from selenium.webdriver.common.by import By

print('\n=== 요소 탐색 ===')
tables = s.driver.find_elements(By.TAG_NAME, 'table')
print(f'테이블 수: {len(tables)}')

divs_with_list = s.driver.find_elements(By.CSS_SELECTOR, '[class*="list"], [class*="program"], [class*="board"]')
print(f'리스트 관련 div 수: {len(divs_with_list)}')

for div in divs_with_list[:5]:
    print(f'  - {div.get_attribute("class")}')

# 로그인 확인
login_check = s.driver.find_elements(By.CSS_SELECTOR, '.login, .logout, [class*="login"], [class*="user"]')
print(f'\n로그인 관련 요소: {len(login_check)}')
for elem in login_check[:3]:
    print(f'  - {elem.get_attribute("class")}: {elem.text[:50] if elem.text else "(empty)"}')

s.close()
