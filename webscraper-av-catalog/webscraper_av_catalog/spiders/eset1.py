# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from scrapy.selector import Selector

from datetime import date
from urllib.parse import urlparse
import json
import re
# import itertools

from . import helpers


today  = date.today().isoformat()

class EsetCom(Spider):

    name = 'eset1.com'
    allowed_domains = ['eset.com','nod32adria.com']

    def __init__(self):
        with open('Antivirus/static_data/start_urls/eset_com.txt') as start_urls:
            self.start_urls = list(start_urls)

        super().__init__()

    # Other regional domains
    # > eset.ro
    # Romania
    # > eset.kz
    # Kazakhstan, Armenia, Georgia, Moldova, Kyrgyzstan, Tajikistan
    # Uzbekistan, Turkmenistan
    # > eset.com.cn, nod32store.com
    # China
    # > eset.az
    # Azerbaijan
    # > getnod32.com -- No pricing data
    # Maldives
    # > eset.co.il
    # Palestine

    # Regions directed to international section (eset.com/int)
    # Iceland

#     def start_requests(self):
#         yield Request('https://nod32adria.com/english/order/', callback=self.parse_pricing_table)

#         baseurls = [
#             'https://www.eset.com/at/',
#             'https://www.eset.com/be-nl/',
#             'https://www.eset.com/be-fr/',
#             'https://www.eset.com/dk/',
#             'https://www.eset.com/ee/',
#             'https://www.eset.com/ee-ru/',
#             'https://www.eset.com/de/',
#             'https://www.eset.com/gr/',
#             'https://www.eset.com/gr-en/',
#             'https://www.eset.com/lv/',
#             'https://www.eset.com/lv-ru/',
#             'https://www.eset.com/lu-fr/',
#             'https://www.eset.com/no/',
#             'https://www.eset.com/si/',
#             'https://www.eset.com/se/',
#             'https://www.eset.com/ch-de/',
#             'https://www.eset.com/ch-en/',
#             'https://www.eset.com/ca/',
#             'https://www.eset.com/ca-fr/',
#             'https://www.eset.com/ar/',
#             'https://www.eset.com/bo/',
#             'https://www.eset.com/co/',
#             'https://www.eset.com/cr/',
#             'https://www.eset.com/do/',
#             'https://www.eset.com/ec/',
#             'https://www.eset.com/sv/',
#             'https://www.eset.com/gt/',
#             'https://www.eset.com/hn/',
#             'https://www.eset.com/cl/',
#             'https://www.eset.com/mx/',
#             'https://www.eset.com/ni/',
#             'https://www.eset.com/pa/',
#             'https://www.eset.com/py/',
#             'https://www.eset.com/pe/',
#             'https://www.eset.com/uy/',
#             'https://www.eset.com/ve/',
#             'https://www.eset.com/kh/',
#             'https://www.eset.com/jp/',
#             'https://www.eset.com/la/',
#             'https://www.eset.com/mm/',
#             'https://www.eset.com/kr/',
#             'https://www.eset.com/lk/',
#             'https://www.eset.com/tw/',
#             'https://www.eset.com/th/',
#             'https://www.eset.com/th-en/',
#             'https://www.eset.com/vn-en/',
#             'https://www.eset.com/gh/',
#             'https://www.eset.com/za/',
#             'https://www.eset.com/ng/',
#             'https://www.eset.com/il/'
#         ]
#         products = [
#             'home/antivirus',
#             'home/smart-security-premium',
#             'home/internet-security',
#             'home/mobile-security-android',
#             'home/parental-control-android',
#             'home/smart-tv-security',
#             'business/entry-protection-bundle',
#             'business/advanced-protection-bundle',
#             'business/complete-protection-bundle'
#         ]
#         for baseurl, product in itertools.product(baseurls, products):
#             yield Request(baseurl + product, callback=self.parse_product)

    def parse_pricing_table(self, response):
        for price_table in response.css('.et_pb_toggle'):
            product = price_table.css('h4::text').get()
            for entry in price_table.css('tr')[1:]:
                devs, price, _ = entry.css('td::text').getall()
                price = price.replace(',', '.')
                for country in [
                    'Croatia', 'Bosnia & Herzegovina', 'Serbia', 'North Macedonia',
                    'Montenegro', 'Kosovo', 'Albania'
                ]:
                    yield {
                        'Date': today,
                        'Source': 'nod32adria.com',
                        'Brand': 'ESET',
                        'Country': country,
                        'URL': response.request.url,
                        'Product Name': product,
                        'Devices': devs,
                        'Term': '1 year',
                        'Current Price': price,
                        'Regular Price': price,
                        'Currency': 'EUR'
                    }

    products = {
        'nod32-antivirus': 'NOD32 Antivirus',
        'antivirus': 'NOD32 Antivirus',
        'smart-security-premium': 'Smart Security Premium',
        'internet-security': 'Internet Security',
        'mobile-security-android': 'Mobile Security for Android',
        'parental-control-android': 'Parental Control for Android',
        'smart-tv-security': 'Smart TV Security',
        'entry-protection-bundle': 'PROTECT Entry',
        'advanced-protection-bundle': 'PROTECT Advanced',
        'complete-protection-bundle': 'PROTECT Complete',

        # Danish codenames
        'internetsikkerhed': 'Internet Security',
        'smart-tv-sikkerhed': 'Smart TV Security',
    }
    platforms = {
        'internet-security': 'Windows, Mac, Android',
        'antivirus': 'Windows, Mac',
        'smart-security-premium': 'Windows, Mac, Android',
        
        # Danish codenams
        'internetsikkerhed': 'Windows, Mac, Android',
        'smart-tv-sikkerhed': 'Android',
    }

    def parse(self, response):
        url = urlparse(response.request.url)
        pathl = list(filter(None, url.path.split('/')))
        product = self.products[pathl[-1]]
        country = url.hostname.split('.')[-1]
        if country == 'com':
            country = pathl[0].split('-')[0]
        country = helpers.country_codes[country]
        dev_types = self.platforms[pathl[-1]]

        jsobjs = response.css('script.ppc-data')
        for jsobj in jsobjs:
            data = json.loads(jsobj.css('::text').get())
            for devs, deals in data['devices'].items():
                for term, deal in deals['boxes'].items():
                    price_lable = Selector(text=deal[term]['price'])
                    flat_price = price_lable.css(
                        '.price.flat.obsolete::attr(data-price)'
                    ).get('')
                    flat_price = ''.join(re.findall('[0-9][0-9 .,]+', flat_price))

                    price = price_lable.css('.price::attr(data-price)').get('')
                    price = ''.join(re.findall('[0-9][0-9 .,]+', price))

                    currency = price_lable.css('.currency::text').get()

                    yield {
                        'Date': today,
                        'Source': 'eset.com',
                        'Brand': 'ESET',
                        'Country': country,
                        'Product Name': product,
                        'URL': response.request.url,
                        'Devices': devs,
#                         'Term': term + ' ' + deal[term]['label'],
                        'Term': f'{term} year',
                        'Current Price': price,
                        'Regular Price': flat_price,
                        'Currency': currency,
                        'Device Types': dev_types
                    }