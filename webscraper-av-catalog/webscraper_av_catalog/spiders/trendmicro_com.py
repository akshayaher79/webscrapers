# -*- coding: utf-8 -*-
from scrapy import Spider, Request

# import itertools
import json
import re
from urllib.parse import urlparse
from datetime import date

from . import helpers


today = date.today().isoformat()

class TrendMicroCom(Spider):
    name = 'trendmicro.com'
    allowed_domains = ['trendmicro.com']

    def __init__(self):
        with open('Antivirus/static_data/start_urls/trendmicro_com.txt') as start_urls:
            self.start_urls = list(start_urls)

        super().__init__()

#     def start_requests(self):
#         base_urls = [
#             'https://www.trendmicro.com/en_us/forHome',
#             'https://www.trendmicro.com/pt_br/forHome',
#             'https://www.trendmicro.com/en_ca/forHome',
#             'https://www.trendmicro.com/es_mx/forHome',
#             'https://www.trendmicro.com/en_au/forHome',
#             'https://www.trendmicro.com/en_hk/forHome',
#             'https://www.trendmicro.com/zh_hk/forHome',
#             'https://www.trendmicro.com/en_in/forHome',
#             'https://www.trendmicro.com/in_id/forHome',
#             'https://www.trendmicro.com/ja_jp/forHome',
#             'https://www.trendmicro.com/ko_kr/forHome',
#             'https://www.trendmicro.com/en_my/forHome',
#             'https://www.trendmicro.com/en_nz/forHome',
#             'https://www.trendmicro.com/en_ph/forHome',
#             'https://www.trendmicro.com/en_sg/forHome',
#             'https://www.trendmicro.com/zh_tw/forHome',
#             'https://www.trendmicro.com/th_th/forHome',
#             'https://www.trendmicro.com/vi_vn/forHome',
#             'https://www.trendmicro.com/en_be/forHome',
#             'https://www.trendmicro.com/en_in/forHome',
#             'https://www.trendmicro.com/en_dk/forHome',
#             'https://www.trendmicro.com/de_de/forHome',
#             'https://www.trendmicro.com/es_es/forHome',
#             'https://www.trendmicro.com/fr_fr/forHome',
#             'https://www.trendmicro.com/en_ie/forHome',
#             'https://www.trendmicro.com/it_it/forHome',
#             'https://www.trendmicro.com/en_nl/forHome',
#             'https://www.trendmicro.com/en_no/forHome',
#             'https://www.trendmicro.com/pl_pl/forHome',
#             'https://www.trendmicro.com/ru_ru/forHome',
#             'https://www.trendmicro.com/en_fi/forHome',
#             'https://www.trendmicro.com/en_se/forHome',
#             'https://www.trendmicro.com/tr_tr/forHome',
#             'https://www.trendmicro.com/en_gb/forHome',
#             'https://www.trendmicro.com/en_me/forHome',
#             'https://www.trendmicro.com/en_il/forHome',
#             'https://www.trendmicro.com/en_me/forHome',
#             'https://www.trendmicro.com/en_my/forHome',
#             'https://www.trendmicro.com/en_za/forHome',
#             'https://www.trendmicro.com/en_ae/forHome',
#             'https://www.trendmicro.com/en_me/forHome'
#         ]
#         products = [
#             '/products/premium-security-suite.html',
#             '/products/maximum-security.html',
#             '/products/internet-security.html',
#             '/products/antivirus-plus.html',
#             '/products/antivirus-for-mac.html',
#             '/products/vpn-proxy-one-pro.html',
#             '/products/password-manager.html',
#             '/products/cleaner-one-mac.html',
#         ]

#         for base_url, product in itertools.product(base_urls, products):
#             yield Request(base_url + product, callback=self.parse_product)

    
    products = {
        'premium-security-suite': 'Premium Security Suite',
        'maximum-security': 'Maximum Security',
        'internet-security': 'Internet Security',
        'antivirus-plus': 'Antivirus+ Security',
        'antivirus-for-mac': 'Antivirus for Mac',
        'vpn-proxy-one-pro': 'VPN Proxy One Pro',
        'password-manager': 'Password Manager',
        'cleaner-one-mac': 'Cleaner One Pro',
        'device-security-ultimate': 'Device Security Ultimate',
        'device-security-basic': 'Device Security Basic',
        'pccillin': 'PC-cillin Maximum Security'

    }

    def parse(self, response):
        dev_types = ', '.join(
            i.strip() for i in response.css(
                '.os-icons > .platform-icon::text, '
                'main > div:first-child .col-sm-12.col-md-12.column .row span::text'
            ).getall() if not i.isspace()
        )
        currency = response.css(
            '.properties__locale::text'
        ).get(default='').partition('-')[2]

        pathl = urlparse(response.request.url).path.split('/')
        product = self.products[pathl[-1].rpartition('.')[0]]
        country = helpers.country_codes[pathl[1].split('_')[1]]

        for term_plan in response.css('.other-durations'):
            yield {
                'Date': today,
                'Source': 'trendmicro.com',
                'Brand': 'Trend Micro',
                'Country': country,
                'Product Name': product, 
                'URL': response.request.url,
                'Devices': term_plan.css('::attr(device-seats)').get(),
                'Term': term_plan.css('::attr(device-duration)').get() + ' year',
                'Device Types': dev_types,
                'Current Price': term_plan.css('.device__sales-price::text').get(),
                'Regular Price': term_plan.css('.device__regular-price::text').get(),
                'Currency': currency
            }
