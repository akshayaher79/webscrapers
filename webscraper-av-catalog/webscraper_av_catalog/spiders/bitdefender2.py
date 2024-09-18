# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.selector import Selector

from urllib.parse import urlparse
import re
import json

from datetime import date

from . import helpers


today = date.today().isoformat()

class Bitdefender2(Spider):
    name = 'bitdefender2'
    allowed_domains = [
        'bitdefender.in',
        'bitdefender.com.tr'
    ]

    def __init__(self):
        super().__init__()

        with open('Antivirus/static_data/start_urls/bitdefender2.txt') as start_urls:
            self.start_urls = list(start_urls)

    products = {
        'antivirus-plus': 'Bitdefender Antivirus Plus',
        'family-pack': 'Bitdefender Family Pack',
        'internet-security': 'Bitdefender Internet Security',
        'mobile-security-android': 'Bitdefender Mobile Security',
        'mobile-security': 'Bitdefender Mobile Security',
        'premium-security': 'Bitdefender Premium Security',
        'total-security': 'Bitdefender Total Security',
        'total-security-multi-device': 'Bitdefender Total Security',
        'antivirus-for-mac': 'Bitdefender Antivirus for Mac',
        'bitdefender-antivirus-plus': 'Bitdefender Antivirus Plus',
        'bitdefender-family-pack': 'Bitdefender Family Pack',
        'bitdefender-internet-security': 'Bitdefender Internet Security',
        'bitdefender-mobile-security-android': 'Bitdefender Mobile Security',
        'bitdefender-mobile-security': 'Bitdefender Mobile Security',
        'bitdefender-premium-security': 'Bitdefender Premium Security',
        'bitdefender-total-security': 'Bitdefender Total Security',
        'bitdefender-antivirus-for-mac': 'Bitdefender Antivirus for Mac',
    }

    platforms = {
        'antivirus': 'PC (Windows)',
        'family-pack': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'internet-security': 'Windows',
        'mobile-security-android': 'Android',
        'mobile-security': 'Android',
        'premium-security': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'total-security': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'total-security-multi-device': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'antivirus-for-mac': 'Mac',
        'bitdefender-antivirus-plus': 'PC (Windows)',
        'bitdefender-family-pack': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'bitdefender-internet-security': 'Windows',
        'bitdefender-mobile-security-android': 'Android',
        'bitdefender-mobile-security': 'Android',
        'bitdefender-premium-security': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'bitdefender-total-security': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'bitdefender-antivirus-for-mac': 'Mac',
    }

    def parse(self, response):
        url = urlparse(response.request.url)
        pathl = list(filter(None, url.path.split('/')))

        product = self.products[pathl[-1]]
        country = helpers.country_codes[url.hostname.split('.')[-1]]
        dev_types = self.platforms[pathl[-1]]

        offers = json.loads(
            response.css('.variations_form::attr(data-product_variations)').get()
        )
        currency = Selector(text=offers[0]['price_html']).css('.woocommerce-Price-currencySymbol::text').get()

        for offer in offers:
            devs = offer['attributes'].get('attribute_pa_kullanici-sayisi') or \
                offer['attributes'].get('attribute_pa_number-of-devices') or  \
                offer['attributes'].get('attribute_pa_numpc') or \
                offer['attributes'].get('attribute_pa_num-of-macs') or ''
            devs = re.search('[0-9]+', devs)
            if devs:
                devs = devs.group()

            term = offer['attributes'].get('attribute_pa_yil') or \
                offer['attributes'].get('attribute_pa_periodlicense') or ''
            term = re.search('[0-9]+', term)
            if term:
                term = term.group()

            yield {
                'URL': response.request.url,
                'Date': today,
                'Source': url.hostname,
                'Brand': 'Bitdefender',
                'Country': country,
                'Product Name': product,
                'Current Price': offer['display_price'],
                'Regular Price': offer['display_regular_price'],
                'Devices': devs,
                'Device Types': dev_types,
                'Term': f'{term} year',
                'Currency': currency
            }

