# -*- coding: utf-8 -*-
from scrapy import Spider

from datetime import date
from urllib.parse import urlparse
import re
import json

from . import helpers


today = date.today().isoformat()

class AvgCom(Spider):
    name = 'avg.com'
    allowed_domains = ['avg.com']

    def __init__(self):
        with open('Antivirus/static_data/start_urls/avg_com.txt') as start_urls:
            self.start_urls = list(start_urls)

        super().__init__()

    platforms = {
        'android': 'Android phone/tablet',
        'ios': 'iPhone/iPad',
        'mac': 'Mac',
        'windows': 'PC (Windows)',
        'multi': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)'
    }
    products = {
        'internet-security': 'Internet Security',
        'secure-vpn': 'Secure VPN',
        'ultimate': 'Ultimate'
    }
    def parse(self, response):
        pathl = urlparse(response.request.url).path.split('/')
        country = helpers.country_codes[pathl[1].split('-')[1]]
        product = self.products[pathl[-1]]

        deals = response.css(
            '#top .js-vue-action-box.vue-action-box, '
            '#hero .js-vue-action-box.vue-action-box, '
            '#banner .js-vue-action-box.vue-action-box'
        )

        for deal in deals:
            option = json.loads(deal.css('::attr(data-settings)').get())['options']['option_1']
            devs = option.get('toggler_text') or (option['header_titles'] and option['header_titles'][0])
            devs = re.search('[0-9]+', devs)
            if devs:
                devs = devs.group(0)
            else:
                devs = 1

            for pricing in option['pricelist'].values():
                yield {
                    'Date': today,
                    'Source': 'avg.com',
                    'Brand': 'AVG',
                    'Country': country,
                    'Product Name': product,
                    'URL': response.request.url,
                    'Devices': devs,
                    'Device Types': self.platforms[option.get('platform')],
                    'Term': '1 year',
                    'Current Price': float(pricing['realPriceRoundedPerMonth']) * 12,
                    'Regular Price': float(pricing['priceRoundedPerMonth']) * 12,
                    'Currency': pricing['currency']
                }

        if not deals:
            yield {
                'Date': today,
                'Brand': 'AVG',
                'Country': country,
                'Product Name': product,
                'Source': 'avg.com',
                'URL': response.request.url,
                'Current Price': 'Free',
                'Regular Price': 'Free',
                'Currency': 'NA',
                'Devices': 'NA',
                'Device Types': '-',
                'Term': 'NA'
            }
