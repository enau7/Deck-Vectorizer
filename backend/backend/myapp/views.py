from django.shortcuts import render
from django.http import HttpResponse
from .models import TodoItem
from deck_scraper.deck_scraper import DeckScraper, MultiDeckScraper
import json
from umap import UMAP
import numpy as np
import pandas as pd
import os
from django.conf import settings
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

# Create your views here.
def home(request):
    url = request.GET.get("decklist_link")
    if url and (len(url) > 0):
        mds = MultiDeckScraper([url])
        decklist = mds.scrape()
    else:
        decklist = ""
    return render(request, "home.html", {"decklist": decklist})

def get_decklist(request, url):
    mds = DeckScraper()
    deck = mds.scrape(url)
    with open(os.path.join(settings.BASE_DIR, 'myapp/static/json/card_embeddings.json'), "r") as f:
        card_embeddings = json.load(f)

    return HttpResponse(json.dumps(card_embeddings))

ds = DeckScraper()

def get_card_vectors(request, decklist):

    # Get card names and embeddings
    deck = ds.scrape(decklist)
    with open(os.path.join(settings.BASE_DIR, 'myapp/static/json/card_embeddings.json'), "r") as f:
        card_embeddings = json.load(f)
    decklist_cards = deck["deck"].keys()
    decklist_embeddings = {card: card_embeddings[card] for card in decklist_cards if card in card_embeddings}
    card_names = list(decklist_embeddings.keys())
    embeddings = [decklist_embeddings[name]["embedding"] for name in card_names]
    oracle_texts = [decklist_embeddings[name]["oracle_text"] for name in card_names]

    print("Decklist Pulled...")

    # Get UMAP 2D projections of the card embeddings
    umap = UMAP(n_components=2, n_neighbors=len(card_names)//8, min_dist=0.1, metric='cosine')
    embeddings_2d = umap.fit_transform(np.array(embeddings))

    # Divide the space into K clusters and assign colors to each cluster
    best_silhouette = -1
    for n_clusters in range(2, min(8, len(decklist_cards))):
        clusters = SpectralClustering(n_clusters=n_clusters, random_state=42)
        test_cluster_labels = clusters.fit_predict(embeddings_2d)
        silhouette = silhouette_score(embeddings, test_cluster_labels)
        if silhouette > best_silhouette:
            best_silhouette = silhouette
            cluster_labels = test_cluster_labels

    # PCA to rotate data along dominant axes
    pca = PCA(n_components=2)
    embeddings_2d = pca.fit_transform(embeddings_2d)

    # Turn cluster labels into hex colors
    cluster_colors = {i: f"#{np.random.randint(0, 0xFFFFFF):06x}" for i in set(cluster_labels)}

    print("Clustering Finished...")

    # Get relative word frequencies
    bags = [" ".join([oracle_texts[n] for n in range(len(oracle_texts)) if cluster_labels[n] == label]) for label in set(cluster_labels)]
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 3),
        smooth_idf=False,
        max_df=3*1/len(set(cluster_labels)),
        min_df=2
    )

    X = vectorizer.fit_transform(bags)
    labels = vectorizer.get_feature_names_out()
    best_labels = []
    for i in range(X.shape[0]):
        row = X[i].toarray().flatten()
        top_indices = row.argsort()[-5:][::-1]
        top_terms = [labels[j] for j in top_indices]
        top_terms = sorted(top_terms, key=lambda x: len(x.split(" ")), reverse=True)
        print(top_terms)
        best_labels.append(top_terms)
    #print(best_labels)

    # Scale vectors to 0 to 1 for better visualization
    min_vec = np.min(embeddings_2d, axis=0)
    max_vec = np.max(embeddings_2d, axis=0)
    scaled_vectors = (embeddings_2d - min_vec) / (max_vec - min_vec)

    # Return as dictionary
    card_data = {}
    for i, card_name in enumerate(card_names):
        card_data[card_name] = {
            "embedding": decklist_embeddings[card_name],
            "position": (scaled_vectors[i]).tolist(),
            "color": cluster_colors[cluster_labels[i]]
        }

    return HttpResponse(json.dumps(card_data))

def todos(request):
    items = TodoItem.objects.all()
    return render(request, "todos.html", {"todos": items})