from deck_scraper.scraper import Scraper
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests
import time

class MoxfieldScraper(Scraper):
    def __init__(self, url, driver=None, banned=list()):
        super().__init__(url=url,
                         driver=driver or webdriver.Chrome(),
                         waiting_class_name="decklist-card")
        
    def get_commander(self):
        try:
            return super().scrape(indexstart='Commander (', indexend=')')[0]
        except:
            return None
    
    def get_counts(self):
        WebDriverWait(self.driver, 10).until(
            EC.any_of(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "decklist-card-quantity")),
                EC.presence_of_all_elements_located((By.CLASS_NAME, "dcD5V3uk1cjCKIMHR5hC"))
            )
        )
        values = list()
        for el in self.driver.find_elements(By.CLASS_NAME, "decklist-card-quantity"):
            try:
                values.append(int(el.get_attribute("innerHTML")[1:]))
            except:
                values.append(0)
        for el in self.driver.find_elements(By.CLASS_NAME, "dcD5V3uk1cjCKIMHR5hC"):
            values.append(int(el.get_attribute("innerText")))
        return values

    def get_deck(self):
        output = list()
        WebDriverWait(self.driver, 10).until(
            EC.any_of(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "table-deck-row-link")),
                EC.presence_of_all_elements_located((By.CLASS_NAME, "decklist-card-phantomsearch"))
            )
        )
        for el in self.driver.find_elements(By.CLASS_NAME, "table-deck-row-link"):
            words = el.find_elements(By.CLASS_NAME, "underline")
            name = "".join([word.get_attribute("innerHTML") for word in words])
            if len(name) > 0:
                output.append(name)
        for el in self.driver.find_elements(By.CLASS_NAME, "decklist-card-phantomsearch"):
            output.append(el.get_attribute("innerText"))
        return output
        
class ArchidektScraper():
    def __init__(self, url):
        self.url = url
        
    def webtext(self):
        base_url = "https://archidekt.com/api/decks/"
        deck_id = self.url.split("/")[-2]
        response = requests.get(base_url + deck_id)
        self.text = response.text
        print("HERE")
        print(self.text)
        print("THERE")
        
    def get_commander(self):
        pass
    
    def get_deck(self):
        pass

    def get_counts(self):
        pass
        
class TopdeckScraper(Scraper):
    def __init__(self, url, driver=None, banned=list()):
        super().__init__(url=url,
                         driver=driver or webdriver.Chrome(),
                         waiting_class_name="type-header")
        
    def get_commander(self):
        return " / ".join(super().scrape(indexstart='<div class="commander-card" data-name="',
                              indexend='"'))
    
    def get_deck(self):
        return super().scrape(indexstart='data-name="',
                              indexend='"')
        
SCRAPER_DICT = {"moxfield": MoxfieldScraper,
                "archidekt": ArchidektScraper,
                "topdeck": TopdeckScraper}

class DeckScraper():
    def __init__(self, driver=None):
        self.driver = webdriver.Chrome()

    def scrape(self, url):
        for service in SCRAPER_DICT.keys():
            if url.find(service) != -1:
                
                # Load scraper
                scraper_class = SCRAPER_DICT[service]
                scraper = scraper_class(url=url, driver=self.driver) if self.driver else scraper_class(url=url)
                scraper.webtext()

                # Get commander, deck, and counts from the scraper
                commander = scraper.get_commander()
                counts = scraper.get_counts()
                deck = scraper.get_deck()

                # Format to dictionary
                decklist = {"commander": commander,
                            "deck": dict(zip(deck, counts))}
                return decklist
            
        raise TypeError(f"Decklist provider not supported: {url}.")

class MultiDeckScraper():

    def __init__(self, urls=list):
        self.urls = urls
        self.scraper = DeckScraper()

    def scrape(self) -> list[dict]:
        decks = list()
        for url in self.urls:
            decklist = self.scraper.scrape(url)
            decks.append(decklist)
        return decks