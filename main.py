
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
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        
    def library(self):
        self.driver.get("https://library.hoseo.ac.kr/#/bbs/notice?offset=0&max=200")
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ikc-item")))
        elements = {
            "이름": self.driver.find_elements(By.CLASS_NAME, "ikc-item-title"),
            "링크": [element.get_attribute("href") for element in self.driver.find_elements(By.CLASS_NAME, "ikc-item-title")]
        }
        for name, link in zip(elements["이름"], elements["링크"]):
            print(f"이름: {name.text}, 링크: {link}")

    def main_pg(self):
        self.driver.get("https://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=0&schCategorycode=CTG_17082400011&schKeytype=subject&schKeyword=&pageIndex=2")

    def cando(self):
        self.driver.get("https://cando.hoseo.ac.kr/Community/Notice/NoticeList.aspx")
def main():
    manager = webdriverManager()
    manager.library()
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
