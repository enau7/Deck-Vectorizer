"""Run this script to add oracle_cards.json and card_embeddings.json to the directory of this file."""

import requests
import argparse
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from inspect import getsourcefile
from os.path import abspath, isfile
from pathlib import Path

# Argparse setup
parser = argparse.ArgumentParser(description='Fetch and process card data from Scryfall API.')
parser.add_argument('-f',
                    '--force',
                    action='store_true',
                    help='Override existing processed file')
args = parser.parse_args()

# Path Setup
base_path = Path(abspath(getsourcefile(lambda:0))).parent

# Flag to rewrite files.
REWRITE = args.force
REFETCH = False

# Get bulk data uri and determine if should rewrite files based on metadata.
bulk_uri = "https://api.scryfall.com/bulk-data"
response = requests.get(bulk_uri)
data = json.loads(response.text)
metadata = {"last_updated": data["data"][0]["updated_at"]}
metadata_path = base_path / "metadata.json"
metadata_exists = isfile(metadata_path)
if metadata_exists:
    # Get old metadata and compare last_updated to determine rewrite.
    with open(metadata_path, "r") as f:
        old_metadata = json.load(f)
        if old_metadata["last_updated"] != metadata["last_updated"]:
            REFETCH = True
            REWRITE = True
else:
    REWRITE = True

# Update metadata file.
with open(metadata_path, "w") as f:
        json.dump(metadata, f)

# File Setup
raw_url = [item["download_uri"] for item in data["data"] if item["name"] == "Oracle Cards"][0]
raw_path = base_path / "oracle_cards.json"
raw_file_exists = isfile(raw_path)
processed_path = base_path / "card_embeddings.json"
processed_file_exists = isfile(processed_path)

# If the file doesn't exist or we should rewrite it, then fetch the file from scryfall
if (not raw_file_exists) or REFETCH:
    print("Fetching raw data from Scryfall...")
    response = requests.get(raw_url)
    with open(raw_path, "w") as f:
        f.write(response.text)
    REWRITE = True
else:
    print("Raw file already exists and is up to date. No fetch needed.")

# Load raw data and calculate embeddings
if (not processed_file_exists) or REWRITE:
    print("Processing raw data and calculating embeddings...")
    with open(raw_path) as f:
        data = pd.DataFrame(json.load(f))

        # Get and format data 
        names = data["name"].values
        oracle_texts = list()
        images = list()
        for i, row in data.iterrows():
            # Oracle text
            if type(row["oracle_text"]) == str:
                oracle_texts.append(row["oracle_text"])
            elif type(row["card_faces"]) == list:
                oracle_texts.append("\n".join([face["oracle_text"] for face in row["card_faces"]]))
            else:
                oracle_texts.append("")

            # Card images
            if type(row["image_uris"]) == dict:
                images.append(row["image_uris"]["normal"])
            elif type(row["card_faces"]) == list:
                images.append(row["card_faces"][0]["image_uris"]["normal"])
            else:
                images.append("")

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
else:
    print("Processed file already exists and is up to date. No processing needed.")