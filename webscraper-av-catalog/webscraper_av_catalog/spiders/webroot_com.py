# -*- coding: utf-8 -*-
from scrapy import Spider, Request

import json
import itertools
from urllib.parse import urlparse, urlencode
from datetime import date

from . import helpers


today = date.today().isoformat()

class WebRoot(Spider):
    name = 'webroot.com'
    allowed_domains = ['webroot.com']

    def __init__(self):
        with open('Antivirus/static_data/start_urls/webroot_com.txt') as start_urls:
            self.start_urls = list(start_urls)

        super().__init__()
#     def start_requests(self):
#         base_urls = [
#             'https://www.webroot.com/au/en',
#             'https://www.webroot.com/ca/en',
#             'https://www.webroot.com/in/en',
#             'https://www.webroot.com/ie/en',
#             'https://www.webroot.com/nz/en',
#             'https://www.webroot.com/za/en',
#             'https://www.webroot.com/gb/en',
#             'https://www.webroot.com/us/en'
#         ]
#         products = [
#             '/home/products/av',
#             '/home/products/isp',
#             '/home/products/complete',
#             '/home/products/gamer-av',
#             '/home/products/family'
#         ]

#         for base_url, product in itertools.product(base_urls, products):
#             yield Request(base_url + product, callback=self.parse_options)

    def parse(self, response):
        pathl = urlparse(response.request.url).path.split('/')
        country = helpers.country_codes[pathl[1]]
        devtypes = response.css('.product-block .device-types::text').get()
        locale = pathl[2] + '_' + pathl[1].upper()
        for deal in response.css('.product-block, .col-xs-12[data-options]'):
            options = json.loads(
                deal.css('::attr(data-options)').get()
            )
            for devs, term in itertools.product(options.get('seats') or options['licence_seats'], options['years']):
                # Crawl onto a dynamic resource with the options collected from this page.
                query = {
                    'locale': locale,
                    'items[0][license_category_name]': options['product'],
                    'items[0][license_seats]': devs,
                    'items[0][years]': term,
    #                 'items[0][license_attribute_license_value]': '11',
    #                 'items[0][category_type_name]': 'full',
    #                 'items[0][item_hierarchy_id]': '1',
    #                 'items[0][message_key]': '94B98A9C-CF27-4A95-9503-0236131D8F73',
    #                 'license_attribute_license_value': '11'
                }
                yield Request(
                    'https://cartapi.webroot.com/cart/bundle-pricing?' + urlencode(query),
                    callback=self.parse_offer,
                    cb_kwargs={
                        'Devices': devs,
                        'Term': f'{term} year',
                        'Country': country,
                        'URL': response.request.url,
                        'Date': today,
                        'Source': 'webroot.com',
                        'Brand': 'Webroot',
                        'Device Types': devtypes
                    }
                )

    def parse_offer(self, response, **item):
        data = response.json()
        item['Current Price'] = data['items'][0]['list_price']
        item['Regular Price'] = data['items'][0]['equivalent_year_price']
        item['Currency'] = data['currency_code']
        item['Product Name'] = data['items'][0]['license_category_description']
        yield item
