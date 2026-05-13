# CardPond: Live Data Analytics for Magic: The Gathering Decks

**CardPond** is a full-stack Django web application that analyzes **Magic: The Gathering** decklists by using machine learning to graph mechanical relationships between cards.

Cardpond helps users better understand decklists by plotting relationships between cards in the dashboard. The idea is that cards close together are mechanically similar, and clusters of cards show the themes and relations of a deck.

Cardpond works by using **SentenceTransformers** to embed card text into high-dimentional vectors. Then, **UMAP** applies dimentionality reduction for 2D visualization in real time, preserving both local and global structure to represent semantic relationships.

- **Live Demo:** [https://cardpond-i1un7.sevalla.app/](https://cardpond-i1un7.sevalla.app/)
- **Tech Stack:** Django · SentenceTransformers · UMAP-Learn · Python ·
JavaScript · HTML+CSS · Python
- **Hosting:** Sevalla (Postgres 18) → transitioning to AWS

## How It Works

1.  User uploads/pastes a decklist.
2.  Backend scrapes decklist or interfaces with a public API to fetch decklist.
3.  Frontend receives precomputed embedding.
4.  UMAP transforms embeddings into 2D live.
5.  Clusters are grouped and colored using spectral clustering.
6.  Frontend renders an interactive scatterplot.

## System Architecture

    Preprocessing Pipeline
    │
    ├── Card Data - https://scryfall.com/docs/api
    ├── Embeddings precomputed using SentenceTransformers.
    └── Embeddings, card name, text and image uri saved to JSON file.

    Django App
    │
    ├── REST API Backend
    │   │
    │   ├── Deck scraper/fetcher gets decklist.
    │   ├── JSON/Database provides embeddings from card name (unique identifier for MTG).
    │   ├── Dimensionality Reduction (UMAP).
    │   └── Clusters generated (Spectral Clustering)
    │
    └── HTML/CSS/JS Frontend
        │
        ├── Each request stored in session (Deck fetcher → Embeddings → Reduction → Clustering)
        ├── Status element shows computation step.
        └── Interactive Visualization shows result.

    Postgres Database
    │
    └── Stores session and user information.

## Roadmap

-   Containerize with Docker for Git LFS.
-   Better CI/CD and testing.
-   "Recently visited" decklists.
-   Card neighborhood visualization.
-   Vector card search.