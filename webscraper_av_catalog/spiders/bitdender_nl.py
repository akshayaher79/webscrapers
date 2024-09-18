# -*- coding: utf-8 -*-
from scrapy import Spider, Request

import re
import json
from urllib.parse import urlparse, urlunparse, urlencode, quote as urlquote

from datetime import date

from . import helpers


today = date.today().isoformat()

class Bitdefender1(Spider):
    name = 'bitdefender.nl'
    allowed_domains = ['bitdefender.nl']

    def __init__(self):
        super().__init__()

        with open('Antivirus/static_data/start_urls/bitdefender_nl.txt') as start_urls:
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

#  https://checkout-service.bitdefender.com/v1/product/variations/price?product_id=com.bitdefender.cl.tsmd
#  https://checkout-service.bitdefender.com/v1/product/variations/price?product_id=com.bitdefender.cl.av&campaign=SecurityTrust2022
 
    def parse(self, response):
        url = urlparse(response.request.url)
        pathl = list(filter(None, url.path.split('/')))

        product_fn = pathl[-1].rpartition('.')[0]

        country_code = url.hostname.split('.')[-1]
        country = helpers.country_codes[country_code]

        query = {
            'product_id': f'com.bitdefender.cl.{self.product_ids[product_fn]}'
        }
        headers = {
            'authority': 'checkout-service.bitdefender.com',
            'accept': '*/*',
            'path': '/v1/product/variations/price?product_id=com.bitdefender.cl.av&campaign=SecurityTrust2022',
            'accept-language': 'en-IN,en-GB;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': f'https://{url.hostname}',
            'pragma': 'no-cache',
            'referer': response.request.url,
            'x-requested-with': 'XMLHttpRequest'
        }
        yield Request(
            urlunparse(
                ('https', 'checkout-service.bitdefender.com', 'v1/product/variations/price' , '', urlencode(query), '')
            ),
            method='GET',
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

        product = response.json()['payload']['payload']
        for variation_group in product.values():
            term = variation_group['billing_period']
            for variation in variation_group['pricing'].values():
                currency = variation['currency']
                reg_price = variation['price']
                cur_price = variation['total']
                devs = variation['devices_no']
                yield {
                    'Current Price': cur_price,
                    'Regular Price': reg_price,
                    'Currency': currency,
                    'Devices': devs,
                    'Term': term,
                    **item
                }

