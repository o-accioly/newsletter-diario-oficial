import logging
import schedule

import datetime, time
import pytz

import pymsteams

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

from dotenv import load_dotenv
from os import getenv

load_dotenv()


logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.INFO)

BASE_URL = "https://www.in.gov.br"
SEARCH_TERMS = getenv("SEARCH_TERMS")
WEBHOOK_URL = getenv("TEAMS_URL")


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

def fetch_daily_article():
    selenium_manager = SeleniumManager()
    
    articles_data = []
    
    for term in SEARCH_TERMS.split("|"):
        url = f"https://www.in.gov.br/consulta/-/buscar/dou?q={term}&s=todos&exactDate=dia&sortType=0"

        logging.info(f"Pesquisando {term} no site do DOU")
        
        page_source = selenium_manager.fetch_page(url)
        
        soup = BeautifulSoup(page_source, "html.parser")
        
        try:
            articles = soup.find('div', class_='resultados-wrapper').find_all('div', class_='resultado')
            logging.info(f"Artigos encontrados com '{term}': {len(articles)}")
        except AttributeError:
            logging.info(f"Nenhum artigo encontrado com '{term}'")
            continue
            
        for article in articles:
            title = article.h5.text.strip()
            
            link = article.a['href']
            link = BASE_URL + link
            
            resume = article.p.text.strip()
            
            breadcrumbs = article.ol.find_all('li')
            breadcrumbs = [breadcrumb.text.strip() for breadcrumb in breadcrumbs]
            
            edition = breadcrumbs.pop(-1)
            
            breadcrumbs = ' > '.join(breadcrumbs)
            
            for article in articles_data:
                if article['link'] == link:
                    break
            else:
                articles_data.append({
                    "title": title,
                    "link": link,
                    "resume": resume,
                    "breadcrumbs": breadcrumbs,
                    "edition": edition,
                    "term": term
                })
        
    selenium_manager.close()
    
    if len(articles_data) == 0:
        logging.info("Nenhum artigo encontrado")
        return
    
    else:
        logging.info(f"Total de artigos encontrados: {len(articles_data)}")
    
    return articles_data
        
def teams_webhook(articles_data):
    logging.info("Enviando artigos para o Teams")
    
    for article in articles_data:
        msg = pymsteams.connectorcard(WEBHOOK_URL)
        
        msg.title(article['title'])
        
        msg.text(f"{article['resume']}\n\n\n\n")
        
        infos_card = pymsteams.cardsection()
        
        infos_card.title("Informações sobre o artigo")
        
        infos_card.addFact("Seção", article['breadcrumbs'])
        infos_card.addFact("Edição", article['edition'])
        infos_card.linkButton("Ver artigo", article['link'])
        
        msg.addSection(infos_card)
        
        msg.send()

def teams_webhook_not_found():
    logging.info("Enviando mensagem de nenhum artigo encontrado")
    
    msg = pymsteams.connectorcard(WEBHOOK_URL)
    
    msg.title("Nenhum artigo encontrado")
    
    msg.text("Nenhum artigo foi encontrado hoje")
    
    msg.send()
        
def job():
    logging.info("Iniciando a busca por artigos")
    
    articles_data = fetch_daily_article()
    
    if articles_data:
        teams_webhook(articles_data)
    else:
        teams_webhook_not_found()
        
    logging.info("Busca finalizada")
        
timezone = pytz.timezone(getenv("TIMEZONE", "America/Sao_Paulo"))

extraction_hour = getenv("EXTRACTION_HOUR", "09:00")
extraction_time = datetime.strptime(extraction_hour, "%H:%M").time().strftime("%H:%M")

schedule.every().day.at(extraction_time).do(job)

logging.info("Iniciando o serviço de newsletter")

while True:
    schedule.run_pending()
    time.sleep(30)