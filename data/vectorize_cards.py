import json
import pandas as pd
from sentence_transformers import SentenceTransformer

with open("repo/data/default_cards.json") as card_data:
    data = pd.DataFrame(json.load(card_data))
    
    # Create embeddings for each card using the SentenceTransformer model and store them in a dictionary
    model = SentenceTransformer('all-MiniLM-L6-v2')
    card_embeddings = dict()

    names = data["name"].values
    oracle_texts = [text if type(text) == str else "" for text in data["oracle_text"].values]

    embeddings = model.encode(oracle_texts, show_progress_bar=True)

    card_embeddings = {name: embedding for name, embedding in zip(names, embeddings)}

    # Save the embeddings
    with open("repo/data/card_embeddings.json", "w") as f:
        json.dump({card: embedding.tolist() for card, embedding in card_embeddings.items()}, f)