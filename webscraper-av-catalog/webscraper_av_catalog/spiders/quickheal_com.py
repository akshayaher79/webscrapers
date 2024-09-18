# -*- coding: utf-8 -*-
from scrapy import Spider

from urllib.parse import urlparse
from datetime import date
import re


today = date.today().isoformat()

class QuickHealCom(Spider):
    name = 'quickheal.com'
    allowed_domains = ['quickheal.com']

    def __init__(self):
        with open('Antivirus/static_data/start_urls/quickheal_com.txt') as start_urls:
            self.start_urls = list(start_urls)

    products = {
        'quick-heal-total-security-multi-device': 'Total Security Multi-Device',
        'quick-heal-total-security': 'Quick Heal Total Security',
        'quick-heal-internet-security': 'Quick Heal Internet Security',
        'quick-heal-antivirus-pro': 'Quick Heal AntiVirus Pro',
    }

    platforms = {
        'quick-heal-total-security-multi-device': 'Android phone/tablet, iPhone/iPad, Mac, PC (Windows)',
        'quick-heal-total-security': 'Windows',
        'quick-heal-internet-security': 'Windows',
        'quick-heal-antivirus-pro': 'Windows'
    }

    def parse(self, response):
        pathl = list(filter(None, urlparse(response.request.url).path.split('/')))
        price = response.css('.price-box > .regular-price > .price::text').get()
        term = response.css('#select_37 > option[selected=selected]::text').get()
        devs = response.css('#select_38 > option[selected=selected]::text').get()
        price = ''.join(re.findall('[0-9 .,]+', price))

        yield {
            'Date': today,
            'Source': 'quickeal.com',
            'Brand': 'Quick Heal',
            'Country': 'United States',
            'Product Name': self.products[pathl[0]],
            'URL': response.request.url,
            'Term': term,
            'Devices': devs,
            'Device Types': self.platforms[pathl[0]],
            'Current Price': price,
            'Regular Price': None,
            'Currency': 'USD'
        }
