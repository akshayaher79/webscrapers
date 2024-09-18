from scrapy import Spider, Request

from urllib.parse import urlparse, urlunparse, urlencode
from datetime import date
import re
import csv
import itertools

from . import helpers


today = date.today().isoformat()

class Kaspersky2(Spider):
    name = 'kaspersky2'
    allowed_domains = [
        'algerie.kaspersky.com',
        'kaspersky.tn',
        'kaspersky.ua',

        # Common AJAX resources host
        'secure.avangate.com'
    ]

    platforms = {
        # Kaspersky Antivirus
        'kav_acq': 'Windows PCs',

        # Kaspersky Internet Security
        'kis_acq': 'PC, Mac & Mobile',
        'kisa_acq': 'PC, Mac & Mobile',
#         'kisa_ren': 'PC, Mac, iOS & Android',

        # Kaspersky Total Protection
        'kts_acq': 'PC, Mac and Mobile',
#         'kts_ren': 'PC, Mac and Mobile',

        # Kaspersky Security Cloud
        'kscfr20': 'PC, Mac, iOS & Android',
        'kscp_acq': 'PC, Mac, iOS & Android',
        'kscf_acq': 'PC, Mac, iOS & Android',
#         'kscp_ren': 'PC, Mac, iOS & Android',
#         'kscf_ren': 'PC, Mac, iOS & Android',

        # Kaspersky Secure Connection
        'ksec_acq': 'PC, Mac, iOS & Android',
#         'ksec_ren': 'PC, Mac, iOS & Android',
    }

    products_q = urlencode(
        {
            'codes': [','.join(platforms.keys())],
            'include': ['options']
        }
    )

    def __init__(self):
        with open('Antivirus/static_data/start_urls/kaspersky2.txt') as start_urls:
            self.start_urls = list(start_urls)
        super().__init__()

        with open('Antivirus/static_data/kaspersky2_const.csv') as const:
            self.const = {
                domain: (merchant, country, lang, currency) for
                domain, merchant, country, lang, currency in csv.reader(const)
            }

    def parse(self, response):
        citation = response.css(
            'a::attr(href)'
        ).get()
        url = urlparse(response.request.url)
        headers = {
            'x-avangate-cart': f'merchant="{self.const[url.hostname][0]}" country="{self.const[url.hostname][1]}" '
                               f'language="{self.const[url.hostname][2]}" currency="{self.const[url.hostname][3]}"'
        }

        yield Request(
            urlunparse(
                ('https', 'secure.avangate.com', '/checkout/api/products/', '', self.products_q, '')
            ),
            method='GET',
            headers=headers,
            callback=self.parse_combo_options,
            cb_kwargs={
                'Input URL': response.request.url,
                'URL': f'https://{url.hostname}',
#                 'URL': citation,
                'Date': today,
                'Source': url.hostname,
                'Brand': 'Kaspersky',
                'Country': helpers.country_codes[self.const[url.hostname][1].lower()],
            },
            dont_filter=True,
            meta={
                'dont_itemise_on_400s': True
            }
        )

    def parse_combo_options(self, response, **item):
        for product in response.json()['data']:
            if product['code'] not in self.platforms.keys():
                continue

            term_type_code = product['options']['data'][0]['code']
            devs_type_code = product['options']['data'][1]['code']
            for term, devs in itertools.product(
                product['options']['data'][0]['options']['data'],
                product['options']['data'][1]['options']['data']
            ):
                term_code = term['code']
                devs_code = devs['code']

                term = re.match('(?P<term>\d)_?(?P<time_unit>mon_p|yea_p|m|y).+', term_code)
                if term:
                    if term.group('time_unit') in ['yea_p', 'y']:
                        term = term.group('term') + ' year'
                    else:
                        term = term.group('term') + ' month'
                devs = re.search('\d+', devs_code)
                if devs:
                    devs = devs.group()

                yield Request(
                    urlunparse((
                        'https', 'secure.avangate.com', f'/checkout/api/products/{product["code"]}/price', '',
                        urlencode({
                            term_type_code: term_code,
                            devs_type_code: devs_code
                        }), ''
                    )),
                    headers=response.request.headers,
                    callback=self.parse_price,
                    cb_kwargs={
                        **item,
                        'Term': term,
                        'Devices': devs,
                        'Product Name': product['name'],
                        'Device Types': self.platforms[product['code']]
                    },
                    dont_filter=True,
                    meta={
                        'dont_itemise_on_400s': True
                    }
                )

    def parse_price(self, response, **item):
        price = response.json()
        item['Regular Price'] = price['net']
        item['Current Price'] = price['netDiscounted']
        item['Currency'] = price['currency']
        yield item
