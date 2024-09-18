from scrapy import Spider, Request

from . import helpers

from urllib.parse import urlparse
from datetime import date
import re


today = date.today().isoformat()

class NortonCom(Spider):

    name = 'norton.com'
    allowed_domains = 'norton.com'

    def __init__(self):
        with open('Antivirus/static_data/start_urls/norton_com.txt') as start_urls:
            self.start_urls = list(start_urls)

        super().__init__()

    products = {
        'mobile-security-for-android': 'Norton Mobile Security for Android',
        'mobile-security-for-ios': 'Norton Mobile Security for iOS',
        'norton-360-antivirus-plus': 'Norton AntiVirus Plus',
        'norton-360-deluxe': 'Norton 360 Deluxe',
        'norton-360-for-gamers': 'Norton 360 for Gamers',
        'norton-360-premium': 'Norton 360 Premium',
        'norton-360-standard': 'Norton 360 Standard',
        'norton-secure-vpn': 'Norton Secure VPN',
        'norton-360-lifelock-select': 'Norton 360 Lifelock Select',
        'norton-360-lifelock-advantage': 'Norton 360 Lifelock Advantage',
        'norton-360-lifelock-ultimate-plus': 'Norton 360 Lifelock Ultimate Plus'
    }

    platforms = {
        'mobile-security-for-android': 'Android smartphone or tablet',
        'mobile-security-for-ios': 'iPhones and iPads',
        'norton-360-antivirus-plus': ' PC or Mac',
        'norton-360-deluxe': ' PC, Mac, smartphones o tablets',
        'norton-360-for-gamers': 'PCs, Mac, smartphones or tablets',
        'norton-360-premium': 'PCs, Macs, smartphones, or tablets',
        'norton-360-standard': 'PC, Mac, smartphone or tablet',
        'norton-secure-vpn': 'PC, Mac or mobile device',
        'norton-360-lifelock-select': 'PCs, Macs, smartphones, or tablets',
        'norton-360-lifelock-advantage': 'PCs, Macs, smartphones, or tablets',
        'norton-360-lifelock-ultimate-plus': 'PCs, Macs, smartphones, or tablets'
    }
    device_words = [
        'device',
        'devices',
        'Device',
        'Devices',
        'Dispositivo',
        'Dispositivos',
        'dispositivos',
        'dispositivi',
        'dispositivo',
        'Gerät',
        'Geräte',
        'appareil',
        'appareils',
        'apparaat',
        'apparaten',
        'zařízení',
        'enheder',
        'laitetta',
        'συσκευές',
        '台裝置',
        'eszköz',
        'enhet',
        'enheter',
        'urządzenie',
        'urządzeń',
        'dispozitiv',
        'dispozitive'
    ]

    def parse(self, response):
        url = urlparse(response.request.url)
        country = url.hostname.split('.')[0].split('-')[0]
        if country == 'lam':
            country = 'Latin America'
        elif country == 'malaysia':
            country = 'Malaysia'
        else:
            country = helpers.country_codes[country]

        product_codename = url.path.split('/')[-1]
        product = self.products[product_codename]
        dev_types = self.platforms[product_codename]

        pack_feats = response.css(
            '.hero-par-wrapper .pdd-dropdown,'
            '.parbase.product-data-display .pdd-dropdown,'
            '.pdd-standard-toggle-radiogroup'
        )
        if pack_feats:
            pack_feats = pack_feats[0].css(
                'ul > li > .entitlement-dropdown-title::text, '
                'input.pdd-standard-toggle-radio::attr(value)'
            ).getall()

        self.logger.debug(f'{pack_feats=}')

        for i, pricing in enumerate(
            response.css('.product-data-display, .c-prodhero__entitle-wrap')[0].css(
                '.pdd-transaction-prices, .c-prodhero__pricecont'
            )
        ):
            old_price = pricing.css(
                '.pdd-prices-old-price, .dp__msrp'
            ).xpath('normalize-space()').get(default='')
            new_price = pricing.css(
                '.pdd-prices-current-price, .dp__sale'
            ).xpath('normalize-space()').get(default='')

            currency = new_price[:re.search(r'\d', new_price).start()]
            if not currency: # Assume currency is mentioned after price figure
                currency = new_price[-re.search(r'\d', new_price[::-1]).start():]

            old_price = ''.join(re.findall('[0-9][0-9 .,]+', old_price))
            new_price = ''.join(re.findall('[0-9][0-9 .,]+', new_price))
            term = None
            devs = None
            if len(pack_feats) > i:
                feat = pack_feats[i]
                if any(word in feat for word in self.device_words):
                    devs = re.search('[0-9]+', feat)
                    devs = devs.group(0) if devs else '1'
                else:
                    term_num = re.search('[0-9]+', feat)
                    if term_num:
                        term = term_num.group(0) + ' year'
                    else: term = feat

            yield {
                'Date': today,
                'Source': 'norton.com',
                'Brand': 'Norton',
                'Country': country,
                'Product Name': product,
                'URL': response.request.url,
                'Currency': currency,
                'Term': term,
                'Device Types': dev_types,
                'Current Price': new_price,
                'Regular Price': old_price,
                'Devices': devs
            }

        if not pack_feats:
            yield {
                'Date': today,
                'Source': 'norton.com',
                'Brand': 'Norton',
                'Country': country,
                'Product Name': product,
                'URL': response.request.url,
                'Currency': None,
                'Term': None,
                'Device Types': dev_types,
                'Current Price': None,
                'Regular Price': None,
                'Devices': None
            }
