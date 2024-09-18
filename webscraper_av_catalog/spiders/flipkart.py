# -*- coding: utf-8 -*-
from scrapy import Spider, Request

from datetime import date
from urllib.parse import urlparse
from os import path
import json
# import itertools
import re



class FlipKart(Spider):
    name = 'flipkart.com'
    allowed_domains = 'flipkart.com'

    def __init__(self):
        with open('Antivirus/static_data/start_urls/avast_com.txt') as start_urls:
            self.start_urls = list(start_urls)

        super().__init__()

#    def start_requests(self):
#         baseurls = [''
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
