from scrapy import Spider, Request

from urllib.parse import urlparse, urljoin
from datetime import date
import re
import json

from . import helpers


today = date.today().isoformat()

class Kaspersky3(Spider):
    name = 'kaspersky3'
    allowed_domains = [
        'kaspersky.com',
        'www.kaspersky.com.hk',
        'www.kaspersky.co.kr',
        'www.kaspersky.co.th'
    ]

    platforms = {
        'Kaspersky Anti-Virus': 'Windows PCs',
        'Kaspersky Antivirus': 'Windows PCs',
        'Kaspersky Internet Security': 'PC, Mac & Mobile',
        'Kaspersky Security Cloud Personal': 'PC, Mac, iOS & Android',
        'Kaspersky Security Cloud Family': 'PC, Mac, iOS & Android',
        'Kaspersky Total Security': 'PC, Mac and Mobile',
        'Kaspersky Secure Connection': 'PC, Mac, iOS & Android',
        'Kaspersky Internet Security for Android': 'Android',
        'Kaspersky Internet Security for Mac': 'Mac',
        'Kaspersky Safe Kids': None,
        
    }
    
    def __init__(self):
        with open('Antivirus/static_data/start_urls/kaspersky3.txt') as start_urls:
            self.start_urls = list(start_urls)
        super().__init__()

    def parse(self, response):
        url = urlparse(response.request.url)
        country = helpers.country_codes[url.hostname.split('.')[-1]]
        for listing in response.css('.buyblock-hebrew'):
            product = listing.css('::attr(data-prodname)').get()
            for pack in json.loads(listing.css('::attr(data-purchaseprice)').get())['prices']:
                current_price = pack.get('price')
                regular_price = pack.get('price_striked')
                currency = pack.get('currency')

                term = pack.get('term') or ''
                term = re.search('[0-9]+', term)
                if term:
                    term = term.group() + ' year'

                devs = pack.get('pack') or ''
                devs = re.search('[0-9]+', devs)
                if devs:
                    devs = devs.group()

                yield {
                    'Input URL': response.request.url,
                    'URL': response.request.url,
                    'Date': today,
                    'Source': url.hostname,
                    'Brand': 'Kaspersky',
                    'Product Name': product,
                    'Devices': devs,
                    'Term': term,
                    'Device Types': self.platforms[product],
                    'Current Price': current_price,
                    'Regular Price': regular_price,
                    'Currency': currency,
                    'Country': country
                }
