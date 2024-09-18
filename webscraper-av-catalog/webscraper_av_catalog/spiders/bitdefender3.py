# -*- coding: utf-8 -*-
from scrapy import Spider

from urllib.parse import urlparse
from datetime import date
import itertools
import re

import js2xml

from . import helpers


today = date.today().isoformat()

class Bitdefender3(Spider):
    name = 'bitdefender3'
    allowed_domains = ['bitdefender.co.th', 'bitdefender.vn']

    def __init__(self):
        super().__init__()

        with open(f'Antivirus/static_data/start_urls/bitdefender3.txt') as start_urls:
            self.start_urls = list(start_urls)

    products = {
        'aplus': 'Antivirus Plus',
        'family-pack': 'Family Pack',
        'internet-security': 'Internet Security',
        'mobile-security': 'Mobile Security',
        'premium-security': 'Security Premium',
        'total-security': 'Total Security'
    }
    platforms = {
        'aplus': 'PC (Windows)',
        'family-pack': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'internet-security': 'Windows',
        'mobile-security': 'Android',
        'premium-security': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'total-security': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
    }
    currencies = {
        'th': 'THB',
        'vn': 'VND'
    }

    def parse(self, response):
        url = urlparse(response.request.url)
        pathl = list(filter(None, url.path.split('/')))

        product_codename = pathl[-1].split('.')[0]
        product = self.products[product_codename]

        dev_types = self.platforms[product_codename]

        country_code = url.hostname.split('.')[-1]
        country = helpers.country_codes[country_code]
        currency = self.currencies[country_code]

        js = response.css('#product-options-wrapper > script::text')
        prices = js2xml.parse(js[0].get())
        packs = js2xml.parse(js[1].get())

        terms = packs.xpath(
            '/program/var[@name="spConfig"]/new/arguments/object/property[@name="attributes"]'
            '//object[property[@name="code"]="year"]/property[@name="options"]'
            '/array/object[property[@name="label"]]'
        )
        devss = packs.xpath(
            '/program/var[@name="spConfig"]/new/arguments/object/property[@name="attributes"]'
            '//object[property[@name="code"]="number_device"]/property[@name="options"]'
            '/array/object[property[@name="label"]]'
        )

        if terms and devss:
            for term, devs in itertools.product(terms, devss):
#                 self.logger.debug(f'{term=} {devs=}')

                price_id = set(
                    term.xpath('./property[@name="products"]/array/string/text()')
                ).intersection(
                    set(
                        devs.xpath('./property[@name="products"]/array/string/text()')
                    )
                )
                if price_id:
                    term = re.search('\d+', term.xpath('normalize-space(./property[@name="label"])'))
                    if term:
                        term = term.group() + ' year'

                    devs = re.search('\d+', devs.xpath('normalize-space(./property[@name="label"])'))
                    if devs:
                        devs = devs.group()

                    price = prices.xpath(
                        '/program/var[@name="simpleProducts"]/object/property[@name=$price_id]'
                        '/object',
                        price_id=str(price_id.pop())
                    )
                    cur_price = None
                    reg_price = None
                    if price:
                        price = price.pop()
                        cur_price = price.xpath('./property[@name="price"]/number/@value').pop()
                        reg_price = price.xpath('./property[@name="oldPrice"]/number/@value').pop()
                        
                        
                    yield {
                        'URL': response.request.url,
                        'Date': today,
                        'Source': url.hostname,
                        'Brand': 'Bitdefender',
                        'Country': country,
                        'Product Name': product,
                        'Current Price': cur_price,
                        'Regular Price': reg_price,
                        'Devices': devs,
                        'Device Types': dev_types,
                        'Term': term,
                        'Currency': currency
                    }
        elif terms:
            for term in terms:
#                 self.logger.debug(f'{term=} {devs=}')

                price_id = term.xpath('./property[@name="products"]/array/string/text()')
                if price_id:
                    term = re.search('\d+', term.xpath('normalize-space(./property[@name="label"])'))
                    if term:
                        term = term.group() + ' year'

                    price = prices.xpath(
                        '/program/var[@name="simpleProducts"]/object/property[@name=$price_id]'
                        '/object',
                        price_id=str(price_id.pop())
                    )
                    cur_price = None
                    reg_price = None
                    if price:
                        price = price.pop()
                        cur_price = price.xpath('./property[@name="price"]/number/@value').pop()
                        reg_price = price.xpath('./property[@name="oldPrice"]/number/@value').pop()

                    yield {
                        'URL': response.request.url,
                        'Date': today,
                        'Source': url.hostname,
                        'Brand': 'Bitdefender',
                        'Country': country,
                        'Product Name': product,
                        'Current Price': cur_price,
                        'Regular Price': reg_price,
                        'Devices': None,
                        'Device Types': dev_types,
                        'Term': term,
                        'Currency': currency
                    }

        elif devss:
            for devs in devss:
#                 self.logger.debug(f'{term=} {devs=}')

                price_id = term.xpath('./property[@name="products"]/array/string/text()')
                if price_id:
                    devs = re.search('\d+', devs.xpath('normalize-space(./property[@name="label"])'))
                    if devs:
                        devs = devs.group()

                    price = prices.xpath(
                        '/program/var[@name="simpleProducts"]/object/property[@name=$price_id]'
                        '/object',
                        price_id=str(price_id.pop())
                    )
                    cur_price = None
                    reg_price = None
                    if price:
                        price = price.pop()
                        cur_price = price.xpath('./property[@name="price"]/number/@value').pop()
                        reg_price = price.xpath('./property[@name="oldPrice"]/number/@value').pop()


                    yield {
                        'URL': response.request.url,
                        'Date': today,
                        'Source': url.hostname,
                        'Brand': 'Bitdefender',
                        'Country': country,
                        'Product Name': product,
                        'Current Price': cur_price,
                        'Regular Price': reg_price,
                        'Devices': devs,
                        'Device Types': dev_types,
                        'Term': None,
                        'Currency': currency
                    }
