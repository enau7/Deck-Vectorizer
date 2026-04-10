import json
import requests
base_url = "https://api.scryfall.com/"
headers = {'Content-Type': 'application/json',
           'Accept': 'application/json',
           'User-Agent': 'mtg_deck_analyzer/0.0'}

# Get decklists
data = {"query": "{leaderboard {player {entries {decklist}}}}"}
req = json.loads(requests.post(base_url + 'graphql', json=data, headers=headers).text)
decklists = sum([[entry["decklist"] for entry in player["player"]["entries"]] for player in req["data"]["leaderboard"]], list())

from deck_scraper import MultiDeckScraper
ds = MultiDeckScraper(decklists[:100])
decks = ds.scrape()
print(decks)