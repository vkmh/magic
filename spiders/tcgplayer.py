import requests
import json

from datetime import datetime

from library import re, text
from urlparse import urljoin


def fix_name(name):
    name = name.replace('&#39;', "'")
    if '(' in name:
        return name.split(' (')[0]
    return name


def fix_price(price):
    return price.replace('$', '')

expansion = 'Battle for Zendikar'
source = 'TCGPlayer'
export_url = 'http://127.0.0.1:8000/api/b018c42e6e6f79568a2844440c16f6fd/'
export_data = {
    'source': source,
    'expansion': expansion,
    'date': str(datetime.now().date()),
    'cards': []
}

base_url = 'http://magic.tcgplayer.com/db/search_result.asp?Set_Name=Battle%20for%20Zendikar'
request = requests.get(base_url)
source = request.text

cards_source = re.capture(r'<table width=540 cellpadding=1 cellspacing=0[^>]*?>(.*?)</table>', source, sanitize=False)
cards = re.findall(r'<tr[^>]*?>(.*?)</tr>', cards_source, flags=re.I | re.S)
if not cards:
    raise Exception("Failed to find cards")

for card_source in cards:
    card_stats = card_source.split('</td>')

    url_stub, name = re.capture(r'<a href="([^>]*?)">([^>]*?)</a>', card_stats[0])
    name = fix_name(name)
    url = urljoin(base_url, url_stub)

    if name in ['Mountain', 'Forest', 'Swamp', 'Island', 'Plains']:
        continue

    mana_cost = text.sanitize(card_stats[1])
    rarity = text.sanitize(card_stats[3])
    high = text.sanitize(card_stats[4])
    medium = text.sanitize(card_stats[5])
    low = text.sanitize(card_stats[6])

    if rarity in ['T', ]:
        continue

    print name
    card_data = {
        'name': name,
        'low': fix_price(low),
        'medium': fix_price(medium),
        'high': fix_price(high)
    }
    export_data['cards'].append(card_data)

d = json.dumps(export_data)
post = {'d': d}
requests.post(export_url, data=post)
