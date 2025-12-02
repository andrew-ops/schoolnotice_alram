
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import logging
from datetime import datetime

def print_elements(elements):
    print("\n" + "="*80)
    for i, (title, link, date) in enumerate(zip(elements["제목"], elements["링크"], elements["날짜"]), 1):
        print(f"[{i}] 제목: {title}")
        print(f"    링크: {link}")
        print(f"    날짜: {date}")
        print("-"*80)

class webdriverManager:
    def __init__(self):
        self.driver = None
        self._setup_driver()

    def _setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("disable-blink-features=AutomationControlled")
        options.add_argument("disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--window-size=1920,1080")
        # GCM 관련 에러 메시지 억제
        options.add_argument("--disable-features=GCMDriver")
        options.add_argument("--log-level=3")  # 에러 로그 숨기기
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def library(self):
        """도서관 공지사항 크롤링"""
        self.driver.get("https://library.hoseo.ac.kr/#/bbs/notice?offset=0&max=200")
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ikc-item")))
        
        # 제목과 링크 추출 (ikc-item-title 클래스의 a 태그)
        title_elements = self.driver.find_elements(By.CLASS_NAME, "ikc-item-title")
        titles = [elem.text for elem in title_elements]
        links = [elem.get_attribute("href") for elem in title_elements]
        
        # 날짜 추출 (ikc-item 안의 날짜 정보)
        rows = self.driver.find_elements(By.CLASS_NAME, "ikc-item")
        dates = []
        for row in rows:
            try:
                # 각 행에서 날짜 정보를 찾음
                date_spans = row.find_elements(By.TAG_NAME, "span")
                for span in date_spans:
                    text = span.text
                    # 날짜 형식 확인 (예: 2025.11.25)
                    if re.match(r'\d{4}\.\d{2}\.\d{2}', text):
                        dates.append(text)
                        break
                else:
                    dates.append("날짜 없음")
            except:
                dates.append("날짜 없음")
        
        elements = {
            "제목": titles,
            "링크": links,
            "날짜": dates
        }
        print_elements(elements)
        return elements

    def main_pg(self, page_start=1, page_end=5):
        """호서대 홈페이지 공지사항 크롤링"""
        all_elements = {
            "제목": [],
            "링크": [],
            "날짜": []
        }
        
        base_url = "https://www.hoseo.ac.kr/Home//BBSView.mbz?action=MAPP_1708240139&schIdx="
        
        for page in range(page_start, page_end + 1):
            self.driver.get(f"https://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=0&schCategorycode=CTG_17082400011&schKeytype=subject&schKeyword=&pageIndex={page}")
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.ui-list tbody tr")))
            
            # 각 행(tr)을 순회하며 데이터 추출
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table.ui-list tbody tr")
            
            for row in rows:
                try:
                    # 제목 추출 (board-list-title 클래스의 td 안의 a 태그)
                    title_td = row.find_element(By.CSS_SELECTOR, "td.board-list-title")
                    title_link = title_td.find_element(By.TAG_NAME, "a")
                    title = title_link.text.strip()
                    
                    # onclick에서 게시글 ID 추출하여 링크 생성
                    onclick_attr = title_link.get_attribute("href")
                    # javascript:fn_viewData('93574') 형태에서 ID 추출
                    match = re.search(r"fn_viewData\('(\d+)'\)", onclick_attr)
                    if match:
                        article_id = match.group(1)
                        link = base_url + article_id
                    else:
                        link = "링크 없음"
                    
                    # 날짜 추출 (등록일자 td)
                    date_td = row.find_element(By.CSS_SELECTOR, "td[data-header='등록일자']")
                    date = date_td.text.strip()
                    
                    all_elements["제목"].append(title)
                    all_elements["링크"].append(link)
                    all_elements["날짜"].append(date)
                except Exception as e:
                    continue
        
        print_elements(all_elements)
        return all_elements

    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()

def main():
    manager = webdriverManager()
    try:
        switch = input("1.도서관 2.호서대 홈페이지 3.호서대 포털 4.캔두\n원하는 페이지의 번호를 입력하세요: ")
        if switch == '1':
            manager.library()
        elif switch == '2' or switch == '3':
            manager.main_pg()
        elif switch == '4':
            print("캔두 기능은 아직 구현되지 않았습니다.")
        else:
            print("잘못된 입력입니다.\n다시 시도해 주세요")
            main()
    finally:
        manager.close()

if __name__ == "__main__":
    main()
'''
def library():
    driver = init_driver()
    driver.get("https://library.hoseo.ac.kr/#/bbs/notice?offset=0&max=200")
    wait = WebDriverWait(driver, 10)
    driver.find_element(By.class_NAME, "ikc-item")
    elements = {"이름":driver.find_elements(By.CLASS_NAME, "ikc-item-title"),"번호":driver.find_elements(By.CLASS_NAME, "ikc-flexth")}

def main():
    driver = init_driver()
    for i in range(2, 4):
        driver.get(f"https://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=0&schCategorycode=CTG_17082400011&schKeytype=subject&schKeyword=&pageIndex={i}")#호서대 홈페이지 공지사항||호서대 포털

def cando():
    driver = init_driver()
'''
