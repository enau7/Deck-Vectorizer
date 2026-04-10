from scraper import Scraper
from selenium import webdriver
from selenium.webdriver.common.by import By

class MoxfieldScraper(Scraper):
    def __init__(self, url, driver=None, banned=list()):
        super().__init__(url=url,
                         driver=driver or webdriver.Chrome(),
                         waiting_class_name="decklist-card",
                         banned=banned)
        
    def get_commander(self):
        return super().scrape(indexstart='Commander (',
                              indexend=')')[0]
    
    def get_counts(self):
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
        for el in self.driver.find_elements(By.CLASS_NAME, "table-deck-row-link"):
            words = el.find_elements(By.CLASS_NAME, "underline")
            name = "".join([word.get_attribute("innerHTML") for word in words])
            if len(name) > 0:
                output.append(name)
        for el in self.driver.find_elements(By.CLASS_NAME, "decklist-card-phantomsearch"):
            output.append(el.get_attribute("innerText"))
        return output
        
class ArchidektScraper(Scraper):
    def __init__(self, url, driver=None, banned=list()):
        super().__init__(url=url,
                         driver=driver or webdriver.Chrome(),
                         waiting_class_name="deckCardWrapper_container__PGeKO",
                         banned=banned)
        
    def get_commander(self):
        return super().scrape(indexstart='<meta name="description" content="',
                              indexend=' -')[0]
    
    def get_deck(self):
        return super().scrape(indexstart='<div class="sc-f126c77f-1 lhCxnG" style="opacity: 1;"><span style="font-size: 12px;">',
                              indexend='<')
        
class TopdeckScraper(Scraper):
    def __init__(self, url, driver=None, banned=list()):
        super().__init__(url=url,
                         driver=driver or webdriver.Chrome(),
                         waiting_class_name="type-header",
                         banned=banned)
        
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
        self.driver = driver or webdriver.Chrome()

    def scrape(self, url):
        for service in SCRAPER_DICT.keys():
            if url.find(service) != -1:
                scraper = SCRAPER_DICT[service](url=url, driver=self.driver)
                scraper.webtext()
                commander = scraper.get_commander()
                counts = scraper.get_counts()
                deck = scraper.get_deck()
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

if __name__=="__main__":
    ds = MultiDeckScraper(urls = [
                                  #"https://archidekt.com/decks/21202156/the_weird_one",
                                  #"https://topdeck.gg/deck/the-cookout-2025/hcEuVBwz3UhORLTf590MFTxK4DC2",
                                  #"https://moxfield.com/decks/XtOruYVVu0CDmDzqaKTtkA",
                                  "https://moxfield.com/decks/KuvVgxGyKU-ID0TSOe8jww",
                                #   "https://moxfield.com/decks/6AoOr6RAnEiwQ-y2gMjxVA",
                                  ])
    print(ds.scrape())