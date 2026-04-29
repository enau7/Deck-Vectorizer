from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("todos/", views.todos, name="Todos"),
    path("myapp/get_card_vectors/<path:decklist>/", views.get_card_vectors, name="get_card_vectors"),
]