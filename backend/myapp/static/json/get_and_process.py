"""Run this script to add oracle_cards.json and card_embeddings.json to the directory of this file."""

import requests
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from inspect import getsourcefile
from os.path import abspath, isfile
from pathlib import Path

# Path Setup
base_path = Path(abspath(getsourcefile(lambda:0))).parent

# File Setup
raw_url = "https://data.scryfall.io/oracle-cards/oracle-cards-20260506090237.json"
raw_path = base_path / "oracle_cards.json"
raw_file_exists = isfile(raw_path)
processed_path = base_path / "card_embeddings.json"
REWRITE = False

# If the file doesn't exist or we should rewrite it, then fetch the file from scryfall
if REWRITE or (not raw_file_exists):
    response = requests.get(raw_url)
    with open(raw_path, "w") as f:
        f.write(response.text)
        print("here")

# Load raw data and calculate embeddings
with open(raw_path) as f:
    data = pd.DataFrame(json.load(f))

    # Get and format data 
    names = data["name"].values
    oracle_texts = [text if type(text) == str else "" for text in data["oracle_text"].values]
    images = [src["normal"] if type(src) == dict else "" for src in data["image_uris"].values]

    # ...and calculate embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(oracle_texts, show_progress_bar=True)

    # Put in dictionary
    card_embeddings = {name: {"embedding": embedding.tolist(),
                              "oracle_text": oracle_text,
                              "img_src": image}
                    for name, embedding, oracle_text, image
                    in zip(names, embeddings, oracle_texts, images)}
    
    # Save to json
    with open(processed_path, "w") as f:
        json.dump(card_embeddings, f, indent=2)