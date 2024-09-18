# -*- coding: utf-8 -*-
from scrapy import Spider, Request


from urllib.parse import urlparse, urlunparse, urlencode
from datetime import date
import re
import csv
import json

from . import helpers


today = date.today().isoformat()

class Kaspersky(Spider):
    name = 'kaspersky1'
    allowed_domains = [
        'africa.kaspersky.com',
        'afrique.kaspersky.com',
        'www.kaspersky.com.au',
        'www.kaspersky.de',
        'www.kaspersky.be',
        'www.kaspersky.com.br',
        'www.kaspersky.bg',
        'www.kaspersky.ca',
        'www.kaspersky.com.cn',
        'www.kaspersky.cz',
        'www.kaspersky.dk',
        'www.kaspersky.fi',
        'www.kaspersky.fr',
        'www.kaspersky.com',
        'www.kaspersky.gr',
        'www.kaspersky.hu',
        'www.kaspersky.co.in',
        'www.kaspersky.it',
        'latam.kaspersky.com',
        'me.kaspersky.com',
        'me-en.kaspersky.com',
        'www.kaspersky.ma',
        'www.kaspersky.no',
        'www.kaspersky.pt',
        'www.kaspersky.ro',
        'www.kaspersky.ru',
        'www.kaspersky.co.za',
        'www.kaspersky.es',
        'www.kaspersky.se',
        'www.kaspersky.com.tw',
        'www.kaspersky.nl',
        'www.kaspersky.com.tr',
        'www.kaspersky.co.uk',
        'usa.kaspersky.com',
        'www.kaspersky.com.vn',

        # Common AJAX resources host
        'api-router.kaspersky-labs.com'
    ]

    def __init__(self):
        with open('Antivirus/static_data/start_urls/kaspersky1.txt') as start_urls:
            self.start_urls = list(start_urls)
        super().__init__()
        
        with open('Antivirus/static_data/kaspersky1_resources.csv') as res_index:
            self.res_index = {
                domain: ref for domain, ref in csv.reader(res_index)
            }

    products = {
        'anti-virus': 'Kaspersky Anti-Virus',
        'antivirus': 'Kaspersky Anti-Virus',
        'internet-security': 'Kaspersky Internet Security',
        'total-security': 'Kaspersky Total Security',
        'vpn-secure-connection': 'Kaspersky Secure Connection',
    }

    product_ranges = {
        'security-cloud': (
            'Kaspersky Security Cloud Personal', 'Kaspersky Security Cloud Family'
        ),
        'home-security': (
            'Kaspersky Anti-Virus', 'Kaspersky Internet Security', 'Kaspersky Total Security'
        )
    }

    platforms = {
        'Kaspersky Anti-Virus': 'Windows PCs',
        'Kaspersky Antivirus': 'Windows PCs',
        'Kaspersky Internet Security': 'PC, Mac & Mobile',
        'Kaspersky Security Cloud Personal': 'PC, Mac, iOS & Android',
        'Kaspersky Security Cloud Family': 'PC, Mac, iOS & Android',
        'Kaspersky Total Security': 'PC, Mac and Mobile',
        'Kaspersky Secure Connection': 'PC, Mac, iOS & Android',
    }

    countries = {
        'africa': 'Africa',
        'afrique': 'French Africa',
        'latam': 'Latin America',
        'me': 'Middle East',
        'me-en': 'Middle East (English)',
        'usa': 'US'
    }

    def parse(self, response):
        url = urlparse(response.request.url)

        offering_code = list(filter(None, url.path.split('/')))[-1].split('.')[0]

        domainl = url.hostname.split('.')
        if domainl[-1] == 'com':
            country = self.countries[domainl[0]]
        else:
            country = helpers.country_codes[domainl[-1]]

        res_ref = self.res_index[url.hostname]
        currency = res_ref.split('/')[4].upper()

        product = self.products.get(offering_code)
        if product:
            yield Request(
                urlunparse(
                     # (scheme, netloc, path, params, query, fragment)
                    ('https', 'api-router.kaspersky-labs.com', res_ref, '', urlencode({'product': product}), '')
                ),
                method='GET',
                callback=self.parse_offerings,
                cb_kwargs={
                    'URL': response.request.url,
                    'Date': today,
                    'Source': url.hostname,
                    'Brand': 'Kaspersky',
                    'Country': country,
                    'Currency': currency,
                    'Product Name': product,
                    'Device Types': self.platforms[product]
                },
                meta={'dont_itemise_on_400s': True}
            )
            return

        for product in self.product_ranges[offering_code]:
            yield Request(
                urlunparse(
                     # (scheme, netloc, path, params, query, fragment)
                    ('https', 'api-router.kaspersky-labs.com', res_ref, '', urlencode({'product': product}), '')
                ),
                method='GET',
                callback=self.parse_offerings,
                cb_kwargs={
                    'URL': response.request.url,
                    'Date': today,
                    'Source': url.hostname,
                    'Brand': 'Kaspersky',
                    'Country': country,
                    'Currency': currency,
                    'Product Name': product,
                    'Device Types': self.platforms[product]
                },
                meta={'dont_itemise_on_400s': True}
            )

    def parse_offerings(self, response, **item):
#         self.logger.debug(f'{response.request.body=}')
#         self.logger.debug(f'{response.text=}')

        for product in response.json()['products'][0]['options']:
            item['Current Price'] = product.get('price')
            item['Regular Price'] = product.get('price_striked')
            item['Term'] = product.get('term_duration')
            devs = product.get('pack') or ''
            devs = re.search('[0-9]+', devs)
            item['Devices'] = devs.group() if devs else None

            yield item
