#visualization
from umap import UMAP
import matplotlib.pyplot as plt
import numpy as np
import json
from deck_scraper.deck_scraper import DeckScraper
from sklearn.cluster import KMeans, SpectralClustering

# Create a 2D scatter plot of the card embeddings using UMAP
def visualize_card_embeddings(card_embeddings, labels=None):
    card_names = list(card_embeddings.keys())
    embeddings = list(card_embeddings.values())

    # Generate clusters
    cluster_labels = labels
    if labels is None:
        clusters = SpectralClustering(n_clusters=5, random_state=42)
        cluster_labels = clusters.fit_predict(embeddings)

    # Generate 2D embeddings using UMAP
    umap = UMAP(n_components=2, n_neighbors=20, min_dist=0.1, metric='cosine')
    embeddings_2d = umap.fit_transform(np.array(embeddings))

    plt.figure(figsize=(12, 8))
    plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], c=cluster_labels, cmap='viridis')

    for i, card_name in enumerate(card_names):
        plt.annotate(card_name, (embeddings_2d[i, 0], embeddings_2d[i, 1]))

    plt.title("Card Embeddings Visualized with UMAP")
    plt.xlabel("UMAP Dimension 1")
    plt.ylabel("UMAP Dimension 2")
    plt.show()

if __name__ == "__main__":
    with open("repo/data/card_embeddings.json") as f:
        card_embeddings = json.load(f)
        ds_t = DeckScraper()
        ds_z = DeckScraper()
        traxos = ds_t.scrape("https://moxfield.com/decks/KuvVgxGyKU-ID0TSOe8jww")["deck"].keys()
        zhulodok = ds_z.scrape("https://moxfield.com/decks/bUBJ0wLp8E6pB8c3HFsiog")["deck"].keys()
       
        # Split the cards into three groups: those in both decks, those only in Traxos, and those only in Zhulodok
        t_intersect_z = set(traxos).intersection(set(zhulodok)).intersection(set(card_embeddings.keys()))
        only_traxos = set(traxos).difference(set(zhulodok)).intersection(set(card_embeddings.keys()))
        only_zhulodok = set(zhulodok).difference(set(traxos)).intersection(set(card_embeddings.keys()))

        # Put all cards into a list and make a corresponding list of labels for the clusters
        all_cards = list(t_intersect_z) + list(only_traxos) + list(only_zhulodok)
        labels = [0] * len(t_intersect_z) + [1] * len(only_traxos) + [2] * len(only_zhulodok)
    
        # Get the embeddings for the cards in the combined list
        card_embeddings = {card: card_embeddings[card] for card in all_cards if card in card_embeddings}
        
        visualize_card_embeddings(card_embeddings, labels=labels)