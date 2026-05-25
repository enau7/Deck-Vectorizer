# Django
from django.shortcuts import render
from django.http import HttpResponse
from deck_scraper.deck_scraper.deck_scraper import DeckScraper
from django.conf import settings

# Models
from myapp.models import Card, Deck, DeckCard

# General Utilities
import json
import numpy as np
import pandas as pd

# Machine Learning
from umap import UMAP
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics import silhouette_score

# Error handling
import traceback
import os

# Create your views here.
def developing_locally(request):
    return HttpResponse(str(settings.LOCAL_DEVELOPMENT).lower())

def home(request):
    return render(request, "home.html")

def dashboard(request):
    return render(request, "dashboard.html")

def about(request):
    return render(request, "about.html")

def get_decklist(request, url):
    try:
        deck = DeckScraper().scrape(url)

        commander = deck["commander"]
        name = deck["name"]

        decklist_cards = deck["deck"].keys()
        decklist_embeddings = Card.objects.filter(name__in=decklist_cards).values("name", "embedding", "oracle_text", "img_src")
        decklist_embeddings = {card["name"]: {"embedding": card["embedding"],
                                            "oracle_text": card["oracle_text"],
                                            "img_src": card["img_src"]} for card in decklist_embeddings}
        
        card_names = list(decklist_embeddings.keys())
        embeddings = [decklist_embeddings[name]["embedding"] for name in card_names]
        oracle_texts = [decklist_embeddings[name]["oracle_text"] for name in card_names]
        img_srcs = [decklist_embeddings[name]["img_src"] for name in card_names]

        card_info = {
            "card_names": card_names,
            "embeddings" : embeddings,
            "oracle_texts" : oracle_texts,
            "img_srcs" : img_srcs,
        }
        
        request.session["card_info"] = card_info
        request.session["name"] = name
        request.session["commander"] = commander
        request.session["url"] = url

        return HttpResponse(json.dumps(card_info))
    
    except Exception as e:
        error = traceback.format_exc()
        print(f"Error: {error}")
        return HttpResponse(
            "<pre>" + error + "</pre>",
            status=500
        )

def cluster_decklist(request):

    decklist = request.session["card_info"]

    card_names = decklist["card_names"]
    embeddings = decklist["embeddings"]
    oracle_texts = decklist["oracle_texts"]
    img_srcs = decklist["img_srcs"]

    umap = UMAP(n_components=2, n_neighbors=len(card_names)//8, min_dist=0.1, metric='cosine')
    embeddings_2d = umap.fit_transform(np.array(embeddings))

    # Divide the space into K clusters and assign colors to each cluster
    best_silhouette = -1
    for n_clusters in range(3, min(8, len(card_names))):
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
    unique_labels = list(set(cluster_labels))
    r = 0 # ratio of color wheel. I want to exclude yellows
    hues = [int((i / len(unique_labels) * (1 - r) + r) * 360) for i in range(len(unique_labels))]
    cluster_colors = {l: f"hsl({h}, 70%, 50%)" for l, h in zip(unique_labels, hues)}
    light_colors = {l: f"hsl({h}, 70%, 78%)" for l, h in zip(unique_labels, hues)}

    # Scale vectors to 0 to 1 for better visualization
    min_vec = np.min(embeddings_2d, axis=0)
    max_vec = np.max(embeddings_2d, axis=0)
    scaled_vectors = (embeddings_2d - min_vec) / (max_vec - min_vec)

    # Return as dictionary
    cluster = {}
    for i, card_name in enumerate(card_names):
        cluster[card_name] = {
            "embedding": embeddings[i],
            "position": scaled_vectors[i].astype(float).tolist(),
            "oracle_text": oracle_texts[i],
            "color": cluster_colors[cluster_labels[i]],
            "light_color": light_colors[cluster_labels[i]],
            "img_src": img_srcs[i],
        }

    request.session["cluster"] = cluster

    return HttpResponse(json.dumps(cluster))

def get_cluster_labels(request):

    cluster = request.session["cluster"]
    cluster_values = list(cluster.values())
    cluster_labels = list(set([cluster_values[i]["color"] for i in range(len(cluster_values))]))
    bags = [" subdoc_boundary ".join([cluster_values[n]["oracle_text"] for n in range(len(cluster_values)) if cluster_values[n]["color"] == label]) for label in cluster_labels]

    stop_words = list(ENGLISH_STOP_WORDS.union({"subdoc_boundary"}))

    vectorizer = TfidfVectorizer(
        token_pattern='(?u)\\b\\w\\w\\w+\\b',
        stop_words=stop_words,
        ngram_range=(1, 3),
        smooth_idf=False,
        max_df=3/len(set(cluster_labels)),
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
        best_labels.append((cluster_labels[i], top_terms[0]))

    request.session["cluster_labels"] = best_labels

    return HttpResponse(json.dumps(best_labels))


def save_to_recents(request):
    # Load data
    name = request.session["name"]
    commander = request.session["commander"]
    url = request.session["url"]
    img = Card.objects.filter(name=commander)[0].img_src
    cluster = request.session["cluster"]
    labels = request.session["cluster_labels"]
    recents = request.session.get("recently_visited", [])

    # If already in recents, pop that. Else, pop last element if recents longer than 3.
    urls = {i: d["url"] for i, d in enumerate(recents) if url != d["url"]}
    new_recents = [r for i, r in enumerate(recents) if i in urls.keys()]

    new_recents.insert(0, {
        "name":name,
        "url":url,
        "img":img,
        "cluster":cluster,
        "labels":labels,
    })

    if len(new_recents) > 3:
        new_recents = new_recents[:3]

    request.session["recently_visited"] = new_recents

    return HttpResponse(json.dumps({"status": "success"}))

def get_recents(requests):
    recents = requests.session.get("recently_visited", None)
    if recents is not None:
        return HttpResponse(json.dumps({"status": "found", "recents": recents}))
    else:
        return HttpResponse(json.dumps({"status": "empty"}))

def load_from_recents(requests, loc):
    try:
        recently_visited = requests.session["recently_visited"][loc]
    except Exception as e:
        return HttpResponse({f"Error loading from recently visited: {e}"},404)
    
    requests.session["name"] = recently_visited["name"]
    requests.session["commander"] = recently_visited["commander"]
    requests.session["url"] = recently_visited["url"]
    requests.session["cluster"] = recently_visited["cluster"]
    requests.session["cluster_labels"] = recently_visited["labels"]

    return HttpResponse({f"Success"})

def load_session(request):
    cluster = request.session.get("cluster", None)
    cluster_labels = request.session.get("cluster_labels", None)
    if cluster is not None:
        return HttpResponse(json.dumps({"status": "found", "cluster": cluster, "cluster_labels": cluster_labels}))
    else:
        return HttpResponse(json.dumps({"status": "empty"}))