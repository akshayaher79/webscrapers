# -*- coding: utf-8 -*-
from scrapy import Spider, Request

from . import helpers

from datetime import date
import itertools


today = date.today().isoformat()

class K7Computing(Spider):

    name = 'k7computing.com'
    allowed_domains = 'k7computing.com'

    def start_requests(self):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-IN,en-GB;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Origin": "https://www.k7computing.com",
            "Referer": "https://www.k7computing.com/"
        }

#         for category, country_code in itertools.product(
#             ['home', 'business'], helpers.country_codes.keys()
#         ):
#             yield Request(
#                 f'https://webapi.k7computing.com/api/v2/product/list/{category}/{country_code}',
#                 headers=headers,
#                 meta={"dont_itemise_on_400s": True}
#             )

        yield Request(
            'https://webapi.k7computing.com/api/v2/product/list/home/us',
            headers=headers
        )

    platforms = {
        'windows': 'PC (Windows)',
        'ios': 'iPhone/iPad',
        'linux': 'Linux',
        'android': 'Android phone/tablet',
        'mac': 'Mac'
    }

    def parse(self, response):
        country = helpers.country_codes[
            response.request.url.split('/')[-1]
        ]
        data = response.json()
        for product in data['products'] or []:
            dev_types = ', '.join(
                self.platforms[os] for os in product['settings']['ossupport']
            )
            for deal in product['sku']:
                devs, term = deal['name'].split('/')
                devs = devs.split()[0]
                term = term.split()[0]
                yield {
                    'Date': today,
                    'Source': 'k7computing.com',
                    'Brand': 'K7COMPUTING',
                    'Country': country,
                    'Product Name': product['name'],
                    'URL': response.request.url,
                    'Devices': devs,
                    'Term': f'{term} year',
                    'Device Types': dev_types,
                    'Current Price': deal.get('price'),
                    'Regular Price': deal.get('strike'),
                    'Currency': deal.get('currency')
                }
