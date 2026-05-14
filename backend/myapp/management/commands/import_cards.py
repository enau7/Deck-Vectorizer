from myapp.models import Card, Deck, DeckCard, Metadata
from django.core.management.base import BaseCommand
import json
import ijson

class Command(BaseCommand):
    help = 'Import cards from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '-o',
            '--override',
            action='store_true',
            help='Override existing cards even if they are up to date'
        )

    def handle(self, *args, **options):

        with open('myapp/static/json/metadata.json') as f:
            try:
                metadata_data = json.load(f)
                last_updated = metadata_data.get("last_updated")
                if (last_updated == Metadata.objects.first().last_updated) and (not options['override']):
                    self.stdout.write(self.style.SUCCESS('Cards are already up to date. No import needed.'))
                    return
                else:
                    self.stdout.write(self.style.WARNING('Cards are outdated. Importing new cards...'))
                    Metadata.objects.all().delete()
                    Metadata(last_updated=last_updated).save()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Couldn\'t load metadata: {e}. Data must be imported.'))

        with open('myapp/static/json/card_embeddings.json') as f:
            counter = 0
            for name, data in ijson.kvitems(f, ''):
                if counter % 100 == 0:
                    self.stdout.write(self.style.SUCCESS(f'Importing card {counter}: {name}'))
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