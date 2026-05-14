from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class Card(models.Model):
    name = models.CharField(max_length = 200, unique=True)
    oracle_text = models.TextField()
    embedding = ArrayField(models.FloatField(), size=384)
    img_src = models.URLField()

class Deck(models.Model):
    name = models.CharField(max_length = 200)
    cards = models.ManyToManyField(Card, null=True, blank=True, through='DeckCard')

class DeckCard(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    umap_embedding = ArrayField(models.FloatField(), size=2)

class Metadata(models.Model):
    last_updated = models.CharField(max_length=100) # Easier to compare as string.