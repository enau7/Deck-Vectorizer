import pandas as pd
import json
from sentence_transformers import SentenceTransformer
from util import n_largest_indices

# Load message embeddings from JSON
with open("repo/data/conversation_embeddings.json") as f:
    conversation_embeddings = json.load(f)

    model = SentenceTransformer('all-MiniLM-L6-v2')

    card_name = input("What card are you looking for? ")
    card_embedding = model.encode(card_name)

    similarities = {conv: model.similarity(card_embedding, embedding) for conv, embedding in conversation_embeddings.items()}
    sorted_similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)
    print(sorted_similarities[:3])

# Get most relevant cards from the conversations
with open("repo/data/card_embeddings.json") as f:
    card_embeddings = json.load(f)

    for conv, _ in sorted_similarities[:3]:
        card_similarities = {card: float(model.similarity(conversation_embeddings[conv], embedding)) for card, embedding in card_embeddings.items()}

        most_relevant_cards = {list(card_similarities.keys())[index]: list(card_similarities.values())[index] for index in n_largest_indices(list(card_similarities.values()), 10)}
        print(f"Most relevant cards: {most_relevant_cards}")
    