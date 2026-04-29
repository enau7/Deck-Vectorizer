from django.shortcuts import render
from django.http import HttpResponse
from .models import TodoItem
from deck_scraper.deck_scraper import DeckScraper, MultiDeckScraper
import json
from umap import UMAP
import numpy as np
import os
from django.conf import settings
from sklearn.cluster import KMeans, SpectralClustering

# Create your views here.
def home(request):
    url = request.GET.get("decklist_link")
    if url and (len(url) > 0):
        mds = MultiDeckScraper([url])
        decklist = mds.scrape()
    else:
        decklist = ""
    return render(request, "home.html", {"decklist": decklist})

def get_decklist(request):
    url = request.GET.get("decklist_link")
    if url and (len(url) > 0):
        mds = MultiDeckScraper([url])
        decklist = mds.scrape()
    else:
        decklist = ""
    return HttpResponse(decklist)

def get_card_vectors(request, decklist):
    mds = DeckScraper()
    deck = mds.scrape(decklist)

    card_data = {}

    with open(os.path.join(settings.BASE_DIR, 'card_embeddings.json'), "r") as f:
        card_embeddings = json.load(f)

    decklist_cards = deck["deck"].keys()
    decklist_embeddings = {card: card_embeddings[card] for card in decklist_cards if card in card_embeddings}

    card_names = list(decklist_embeddings.keys())
    embeddings = list(decklist_embeddings.values())

    # Get UMAP 2D projections of the card embeddings
    umap = UMAP(n_components=2, n_neighbors=10, min_dist=0.1, metric='cosine')
    embeddings_2d = umap.fit_transform(np.array(embeddings))

    # Divide the space into K clusters and assign colors to each cluster
    clusters = SpectralClustering(n_clusters=5, random_state=42)
    cluster_labels = clusters.fit_predict(embeddings_2d)

    # Turn cluster labels into hex colors
    cluster_colors = {i: f"#{np.random.randint(0, 0xFFFFFF):06x}" for i in set(cluster_labels)}

    # Scale vectors to 0 to 1 for better visualization
    min_vec = np.min(embeddings_2d, axis=0)
    max_vec = np.max(embeddings_2d, axis=0)
    scaled_vectors = (embeddings_2d - min_vec) / (max_vec - min_vec)

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