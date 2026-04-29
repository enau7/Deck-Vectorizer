from deck_scraper.deck_scraper import DeckScraper, MultiDeckScraper

if __name__=="__main__":
    ds = DeckScraper()
    print(ds.scrape("https://archidekt.com/decks/21202156/the_weird_one"))