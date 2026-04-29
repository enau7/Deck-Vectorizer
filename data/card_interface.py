import json
import pandas as pd
from deck_scraper.deck_scraper import DeckScraper
from sentence_transformers import SentenceTransformer

with open("repo/data/default_cards.json") as card_data:
    data = pd.DataFrame(json.load(card_data))
    ds = DeckScraper()
    decklist = ds.scrape("https://moxfield.com/decks/KuvVgxGyKU-ID0TSOe8jww")
    cards = list(decklist["deck"].keys())
    card_text = {card: data.loc[data["name"] == card, "oracle_text"].iloc[0] for card in cards if card in data["name"].values and data.loc[data["name"] == card, "oracle_text"].iloc[0] is not None}

    # Create embeddings for each card in the decklist using the SentenceTransformer model and store them in a dictionary
    model = SentenceTransformer('all-MiniLM-L6-v2')
    card_embeddings = {card: model.encode(text) for card, text in card_text.items()}
    
    # Get the embedding for "Voltaic Key" and find a list of the 10 most similar cards in the decklist
    # voltaic_key_embedding = card_embeddings["Voltaic Key"]
    # similarities = {card: model.similarity(voltaic_key_embedding, embedding) for card, embedding in card_embeddings.items()}
    # sorted_similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)
    # print(sorted_similarities)

    description = input("What effect are you looking for? ")
    description_embedding = model.encode(description)
    similarities = {card: model.similarity(description_embedding, embedding) for card, embedding in card_embeddings.items()}
    sorted_similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)
    print(sorted_similarities[:10])