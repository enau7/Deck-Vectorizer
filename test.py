from deck_scraper.deck_scraper import DeckScraper
from selenium import webdriver

if __name__=="__main__":
    ds = DeckScraper(driver=webdriver.Chrome())
    print(ds.scrape("https://moxfield.com/decks/sOE8Hduq-kqQ3je7FqD02g"))
    print(ds.scrape("https://moxfield.com/decks/KuvVgxGyKU-ID0TSOe8jww"))
