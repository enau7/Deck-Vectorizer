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
    images = [src if type(src) == str else "" for src in data["image_uris"]["normal"].values]
    embeddings = model.encode(oracle_texts, show_progress_bar=True)

    card_embeddings = {name: {"embedding": embedding.tolist(),
                              "oracle_text": oracle_text,
                              "img_src": images}
                       for name, embedding, oracle_text
                       in zip(names, embeddings, oracle_texts)}

    # Save the embeddings
    with open("repo/data/card_embeddings.json", "w") as f:
        json.dump(card_embeddings, f)