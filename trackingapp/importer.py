import json
from trackingapp.models import Card, Expansion, Source, SourceExpansion, Stock

urls = {
    'TCGPlayer': 'http://tcgplayer.com/',
}


def ingest(import_data):
    json_data = json.loads(import_data)
    source = get_source(json_data['source'])
    date = json_data['date']
    expansion = get_expansion(json_data['expansion'])
    link_source_expansion(source, expansion)

    Stock.objects.filter(source=source, card__expansion=expansion, date=date).update(is_active=False)

    for json_card in json_data['cards']:
        name = json_card['name']
        high = json_card['high']
        medium = json_card['medium']
        low = json_card['low']

        card = get_card(name, expansion)
        Stock.objects.create(
            card=card,
            source=source,
            date=date,
            high=high,
            medium=medium,
            low=low,
            is_active=True
        )


def link_source_expansion(source, expansion):
    SourceExpansion.objects.get_or_create(source=source, expansion=expansion)


def get_expansion(expansion_text):
    expansion, created = Expansion.objects.get_or_create(name=expansion_text)
    return expansion


def get_source(source_text):
    source, created = Source.objects.get_or_create(name=source_text, url=urls[source_text])
    return source


def get_card(name, expansion):
    card, created = Card.objects.get_or_create(name=name, expansion=expansion)
    return card
