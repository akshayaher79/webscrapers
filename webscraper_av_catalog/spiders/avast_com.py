# -*- coding: utf-8 -*-
from scrapy import Spider, Request

from datetime import date
from urllib.parse import urlparse
from os import path
import json
# import itertools
import re

from . import helpers


today = date.today().isoformat()

class AvastCom(Spider):
    name = 'avast.com'
    allowed_domains = ['avast.com', 'avast.ru', 'avast.co.jp', 'avast.ua']

    def __init__(self):
        with open('Antivirus/static_data/start_urls/avast_com.txt') as start_urls:
            self.start_urls = list(start_urls)

        super().__init__()

#    def start_requests(self):
#         baseurls = [
#             'https://www.avast.com/es-ar/',
#             'https://www.avast.com/pt-br/',
#             'https://www.avast.com/en-ca/',
#             'https://www.avast.com/fr-ca/',
#             'https://www.avast.com/es-cl/',
#             'https://www.avast.com/es-co/',
#             'https://www.avast.com/es-us/',
#             'https://www.avast.com/es-mx/',
#             'https://www.avast.com/en-us/',
#             'https://www.avast.com/nl-be/',
#             'https://www.avast.com/fr-be/',
#             'https://www.avast.com/cs-cz/',
#             'https://www.avast.com/da-dk/',
#             'https://www.avast.com/de-de/',
#             'https://www.avast.com/es-es/',
#             'https://www.avast.com/fr-fr/',
#             'https://www.avast.com/it-it/',
#             'https://www.avast.com/hu-hu/',
#             'https://www.avast.com/nl-nl/',
#             'https://www.avast.com/no-no/',
#             'https://www.avast.com/pl-pl/',
#             'https://www.avast.com/pt-pt/',
#             'https://www.avast.com/de-ch/',
#             'https://www.avast.com/cs-sk/',
#             'https://www.avast.com/en-za/',
#             'https://www.avast.com/fr-ch/',
#             'https://www.avast.com/fi-fi/',
#             'https://www.avast.com/sv-se/',
#             'https://www.avast.com/tr-tr/',
#             'https://www.avast.com/en-ae/',
#             'https://www.avast.com/en-gb/',
#             'https://www.avast.com/el-gr/',
#             'https://www.avast.com/he-il/',
#             'https://www.avast.com/ru-kz/',
#             'https://www.avast.com/ro-ro/',
#             'https://www.avast.ru/',
#             'https://www.avast.ua/',
#             'https://www.avast.ua/ru-ua/',
#             'https://www.avast.com/ar-sa/',
#             'https://www.avast.com/ar-ww/',
#             'https://www.avast.com/en-au/',
#             'https://www.avast.com/en-in/',
#             'https://www.avast.com/hi-in/',
#             'https://www.avast.com/en-id/',
#             'https://www.avast.com/id-id/',
#             'https://www.avast.com/en-my/',
#             'https://www.avast.com/ms-my/',
#             'https://www.avast.com/en-nz/',
#             'https://www.avast.com/en-ph/',
#             'https://www.avast.com/tl-ph/',
#             'https://www.avast.com/en-sg/',
#             'https://www.avast.com/vi-vn/',
#             'https://www.avast.co.jp/',
#             'https://www.avast.com/ko-kr/',
#             'https://www.avast.com/zh-cn/',
#             'https://www.avast.com/zh-tw/',
#             'https://www.avast.com/th-th/',
#         ]

#         home_products = [
#             'free-antivirus-download',
#             'premium-security',
#             'ultimate',
#             'secureline-vpn',
#             'antitrack',
#             'secure-browser',
#             'breachguard',
#             'avast-online-security',
#             'cleanup',
#             'driver-updater',
#             'avast-one',
#         ]

#         business_products = [
#             'small-office-protection',
#             'essential',
#             'premium',
#             'ultimate',
#             'patch-management',
#             'cloud-backup-for-small-business',
#             'premium-remote-control',
#             'linux-antivirus',
#             'ccleaner'
#         ]

#         for baseurl, pagename in itertools.product(baseurls, home_products):
#             yield Request(baseurl + pagename, callback=self.parse_home_product)
#         for baseurl, pagename in itertools.product(baseurls, business_products):
#             yield Request(baseurl + pagename, callback=self.parse_business_product)

    products = {
        'free-antivirus-download': 'Free Antivirus',
        'premium-security': 'Premium Security',
        'ultimate': 'Ultimate',
        'secureline-vpn': 'SecureLine VPN',
        'antitrack': 'AntiTrack',
        'secure-browser': 'Secure Browser',
        'breachguard': 'BreachGuard',
        'avast-online-security': 'Online Security and Privacy',
        'cleanup': 'Cleanup',
        'driver-updater': 'Driver Updater',
        'avast-one': 'Avast One',
        'small-office-protection': 'Small Office Protection',
        'essential': 'Essential',
        'premium': 'Premium',
        'patch-management': 'Patch Management',
        'cloud-backup-for-small-business': 'Cloud Backup',
        'premium-remote-control': 'Premium Remote Control',
        'linux-antivirus': 'Linux Antivirus',
        'ccleaner': 'CCleaner'
    }
    platforms = {
        'android': 'Android phone/tablet',
        'ios': 'iPhone/iPad',
        'mac': 'Mac',
        'pc': 'PC (Windows)',
        'windows': 'PC (Windows)',
        'multi': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)'
    }

    def parse(self, response):
        url = urlparse(response.request.url)
        product = self.products[path.split(url.path)[1]]
        country_code = url.hostname.split('.')[-1]
        if country_code == 'com':
            country_code = url.path[4:6]
        country = helpers.country_codes[country_code]

        listings = response.css(
            '#top .js-action-box-row, '
            '#hero .js-action-box-row, '
            '#banner .js-action-box-row'
        )
        for listing in listings:
            for deal in json.loads(listing.css('::attr(data-settings)').get()):
                for option in deal['options'].values():
                    if not option.get('pricelist'):
                        continue

                    devs = option.get('toggler_text') or (option['header_titles'] and option['header_titles'][0])
                    devs = re.search('[0-9]+', devs)
                    devs = devs.group(0) if devs else 1

                    dev_types = self.platforms[option.get('platform') or 'multi']
                    for pricing_plan in option['pricelist'].values():
                        yield {
                            'Date': today,
                            'Source': 'avast.com',
                            'Brand': 'AVAST',
                            'Country': country,
                            'Product Name': product,
                            'URL': response.request.url,
                            'Devices': devs,
                            'Term': '1 year',
                            'Device Types': dev_types,
                            'Current Price': float(pricing_plan['realPriceRoundedPerMonth']) * 12,
                            'Regular Price': float(pricing_plan['priceRoundedPerMonth']) * 12,
                            'Currency': pricing_plan['currency'],
                        }

        if not listings:
            yield {
                'Date': today,
                'Source': 'avast.com',
                'Brand': 'AVAST',
                'Country': country,
                'Product Name': product,
                'URL': response.request.url,
                'Devices': 'NA',
                'Term': 'NA',
                'Device Types': '-',
                'Current Price': '0',
                'Regular Price': '0',
                'Currency': 'NA'
            }
