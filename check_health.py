import logging
import schedule

import time
from datetime import datetime

import pytz

import pymsteams

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

from dotenv import load_dotenv
from os import getenv

import argparse

load_dotenv()


logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.INFO)


class SeleniumManager:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = self._initialize_driver()
    
    def _initialize_driver(self):
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
            
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def fetch_page(self, url):
        self.driver.get(url)
        time.sleep(5)  # Esperar o carregamento da página
        return self.driver.page_source
    
    def close(self):
        self.driver.quit()
        

logging.info("Iniciando o script de verificação de saúde do site")

logging.info("Iniciando o Selenium")
try:
    driver = SeleniumManager()
except Exception as e:
    logging.error("Erro ao iniciar o Selenium")
    logging.error(e)
    exit(1)
    
    
logging.info("Selenium iniciado com sucesso")

parser = argparse.ArgumentParser(description="Verifica a saúde do site")
parser.add_argument("--url", type=str, help="URL do site a ser verificado")
args = parser.parse_args()

print(driver.fetch_page(args.url))

logging.info("Página carregada com sucesso")