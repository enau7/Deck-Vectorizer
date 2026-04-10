from deck_scraper import MultiDeckScraper

mds = MultiDeckScraper(urls=["https://moxfield.com/decks/MLTcxH6tkEyWA2bHmBE7-g","https://moxfield.com/decks/KuvVgxGyKU-ID0TSOe8jww"])

decks = mds.scrape()

deck_1 = decks[0]["deck"]
deck_2 = decks[1]["deck"]

count = 0
for key in deck_1.keys():
    if key in deck_2.keys():
        count += min(deck_1[key], deck_2[key])

print (count/100)