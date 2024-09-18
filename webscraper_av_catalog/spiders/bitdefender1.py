# -*- coding: utf-8 -*-
from scrapy import Spider, Request

import re
import json
from urllib.parse import urlparse, urlencode, quote as urlquote

from datetime import date

from . import helpers


today = date.today().isoformat()

class Bitdefender1(Spider):
    name = 'bitdefender1'
    allowed_domains = [
        'bitdefender.de',
        'bitdefender.fr',
        'bitdefender.be',
        'bitdefender.com.br',
        'bitdefender.it',
        'bitdefender.pt',
        'bitdefender.ro',
        'bitdefender.es',
    ]

    def __init__(self):
        super().__init__()

        with open('Antivirus/static_data/start_urls/bitdefender.txt') as start_urls:
            self.start_urls = list(start_urls)

    products = {
        'antivirus': 'Bitdefender Antivirus Plus',
        'family-pack': 'Bitdefender Family Pack',
        'internet-security': 'Bitdefender Internet Security',
        'mobile-security-android': 'Bitdefender Mobile Security',
        'premium-security': 'Bitdefender Premium Security',
        'total-security': 'Bitdefender Total Security',
        'antivirus-for-mac': 'Bitdefender Antivirus for Mac'
    }

    product_ids = {
        'antivirus': 'av',
        'family-pack': 'fp',
        'internet-security': 'is',
        'mobile-security-android': 'mobile',
        'premium-security': 'ps',
        'total-security': 'tsmd',
        'vpn': 'vpn',
        'antivirus-for-mac': 'mac'
    }

    platforms = {
        'antivirus': 'PC (Windows)',
        'family-pack': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'internet-security': 'Windows',
        'mobile-security-android': 'Android',
        'premium-security': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'total-security': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'antivirus-for-mac': 'Mac',
        'vpn': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)'
    }

    def parse(self, response):
        url = urlparse(response.request.url)
        pathl = list(filter(None, url.path.split('/')))

        product_fn = pathl[-1].rpartition('.')[0]

        country_code = url.hostname.split('.')[-1]
        country = helpers.country_codes[country_code]

        query = {
            'data': repr(
                {'ev': 1, 'product_id': self.product_ids[product_fn]}
            ).replace("'",'"').replace(' ', '')
        }
        headers = {
            'authority': url.hostname,
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-GB, en-US;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': f'https://{url.hostname}',
            'pragma': 'no-cache',
            'referer': response.request.url,
            'x-requested-with': 'XMLHttpRequest'
        }
        yield Request(
            f'https://{url.hostname}/site/Store/ajax',
            body=urlencode(query, quote_via=urlquote),
            method='POST',
            callback=self.parse_pricing,
            cb_kwargs={
                'URL': response.request.url,
                'Date': today,
                'Source': url.hostname,
                'Brand': 'Bitdefender',
                'Country': helpers.country_codes[country_code],
                'Device Types': self.platforms[product_fn],
                'Product Name': self.products[product_fn]
            },
            headers=headers,
            meta={'dont_itemise_on_400s': True}
        )

    def parse_pricing(self, response, **item):
        self.logger.debug(f'{response.request.body=}')
        self.logger.debug(f'{response.text=}')

        product = response.json()['data']['product']
        for variation_group in product['variations'].values():
            for variation in variation_group.values():
                currency = variation['currency_iso']
                price = variation['price']
                slashed_price = variation.get('discount') and variation['discount']['discounted_price']
                
                options = re.match(
                    r'(?P<devs>\d+)u-(?P<term>\d+)(?P<time_unit>[ym])',
                    variation['variation']['variation_name']
                )
                term = options.group('term')
                if options.group('time_unit') == 'm':
                    term = f'{float(term) / 12.0:.1f} year'
                else:
                    term = f'{term} year'

                yield {
                    'Current Price': slashed_price,
                    'Regular Price': price,
                    'Currency': currency,
                    'Devices': options.group('devs'),
                    'Term': term,
                    **item
                }

