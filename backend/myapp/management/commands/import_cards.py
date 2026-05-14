from myapp.models import Card, Deck, DeckCard, Metadata
from django.core.management.base import BaseCommand
import json

class Command(BaseCommand):
    help = 'Import cards from a JSON file'

    def handle(self, *args, **kwargs):

        with open('myapp/static/json/metadata.json') as f:
            try:
                metadata_data = json.load(f)
                last_updated = metadata_data.get("last_updated")
                if last_updated == Metadata.objects.first().last_updated:
                    self.stdout.write(self.style.SUCCESS('Cards are already up to date. No import needed.'))
                    return
                else:
                    self.stdout.write(self.style.WARNING('Cards are outdated. Importing new cards...'))
                    Metadata.objects.all().delete()
                    Metadata(last_updated=last_updated).save()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Couldn\'t load metadata: {e}. Data must be imported.'))

        with open('myapp/static/json/card_embeddings.json') as f:
            cards_data = json.load(f)
            counter = 0
            for name, data in cards_data.items():
                if counter % 100 == 0:
                    self.stdout.write(self.style.SUCCESS(f'Importing card {counter}/{len(cards_data)}: {name}'))
                counter += 1
                try:
                    card = Card(
                        name=name,
                        oracle_text=data['oracle_text'],
                        embedding=data['embedding'],
                        img_src=data['img_src']
                    )
                    card.save()
                except Exception as e:
                    pass
        
        Metadata.objects.all().delete()
        Metadata(last_updated=last_updated).save()