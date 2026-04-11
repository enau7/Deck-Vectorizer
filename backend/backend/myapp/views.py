from django.shortcuts import render, HttpResponse
from .models import TodoItem
from deck_scraper.deck_scraper import MultiDeckScraper

# Create your views here.
def home(request):
    url = request.GET.get("url")
    if url and (len(url) > 0):
        mds = MultiDeckScraper([url])
        decklist = mds.scrape()
    else:
        decklist = ""
    return render(request, "home.html", {"decklist": decklist})

def todos(request):
    items = TodoItem.objects.all()
    return render(request, "todos.html", {"todos": items})