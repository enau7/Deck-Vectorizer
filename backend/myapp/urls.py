from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("myapp/get_card_vectors/<path:decklist>/", views.get_card_vectors, name="get_card_vectors"),
    path("myapp/get_decklist/<path:url>/", views.get_decklist, name="get_decklist"),
    path("myapp/cluster_decklist/", views.cluster_decklist, name="cluster_decklist"),
    path("myapp/get_cluster_labels/", views.get_cluster_labels, name="get_cluster_labels"),
    path("myapp/developing_locally/", views.developing_locally, name="developing_locally")
]