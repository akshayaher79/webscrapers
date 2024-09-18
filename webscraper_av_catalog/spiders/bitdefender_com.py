# -*- coding: utf-8 -*-
from scrapy import Spider, Request

import re
import json
from urllib.error import HTTPError
from urllib.parse import urlparse, urlencode
import urllib.request

from datetime import date

from . import helpers


today = date.today().isoformat()

class BitdefenderCom(Spider):
    name = 'bitdefender.com'
    # Groups of domains are annotated with available resources
    allowed_domains = [
        'bitdefender.com',    # .../countries.json, .../checkout.*
        'bitdefender.com.au', # .../countries.json, .../checkout.*
        'bitdefender.co.uk',  # .../countries.json, .../checkout.*
        'bitdefender.my',   # Server redirects to www.bitdefender.com

#         [Covered by bitdefender1 spider]
#          /site/Store/ajax
#         'bitdefender.de',
#         'bitdefender.fr',
#         'bitdefender.be',
#         'bitdefender.pt',
#         'bitdefender.ro',
#         'bitdefender.it',
#         'bitdefender.com.br',
#         'bitdefender.es',

#         [Covered by bitdefender2 spider]
#          Main document file, JSON attribute value
#         'bitdefender.com.tr',
#         'bitdefender.in',
#         'bitdefender.pl',

#         [Covered by bitdefender3 spider]
#          Main document file, JS variable (simpleProducts) assignment
#          in <script> (#product-options-wrapper > script)
#         'bitdefender.co.th',
#         'bitdefender.vn'

#         [Uncovered]
#         'bitnet.com.hr'  # Sources couldn't be found.
#         'bitdefender.nl', # https://checkout-service.bitdefender.com/v1/product/variations/price
#         'bitdefender.co.jp', # Main document file, <script>
#         'bitdefender.ru', # Access proibited by HaaS provider (Cloudflare)
#         'bitdefender.com.tw', # Website in different format
#         'bitdefender.com.ua', # No brochures on website, siteroot
                                # redirected to solidworks.softico.ua
#         'bitdefender.cz', # AJAX source at document URL
#         'www.bitdefender.gr' # /wp-admin/admin-ajax.php -- AJAX source for
                               # webpages in /bitdefender directory
    ]

    countries = {}

    def __init__(self):
        super().__init__()

        with open('Antivirus/static_data/start_urls/bitdefender_com.txt') as start_urls:
            self.start_urls = list(start_urls)

        self.logger.info('Downlaoding countries indices from target websites to initialise spider.')
        _404_domains = []
        json_err_domains = []
        _200_domains = []
        for domain in self.allowed_domains:
            try:
                with urllib.request.urlopen(
                    urllib.request.Request(
                        f'https://{domain}'
                        '/etc.clientlibs/bitdefender/clientlibs'
                        '/clientlib-site/resources/data/countries.json?v=2',
                        headers={
                            'authority': domain,
                            'accept': 'application/json,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                            'accept-language': 'en-IN,en-GB;q=0.9,en;q=0.8',
                            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) ' \
                                'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                                'Chrome/101.0.4951.54 Safari/537.36'
                        }
                    )
                ) as countries:
                    self.countries.update(json.load(countries)[0])
                    _200_domains.append(domain)
            except HTTPError:
                _404_domains.append(domain)
            except json.decoder.JSONDecodeError:
                json_err_domains.append(domain)

        if _404_domains:
            self.logger.debug(f'countries.json files not found on {", ".join(_404_domains)}')
        if json_err_domains:
            self.logger.debug(f'countries.json malformed on {", ".join(json_err_domains)}')
        self.logger.debug(f'Parsed countries.json files from {", ".join(_200_domains)} into:')
        self.logger.debug(self.countries)

    products = {
        'antivirus': 'Bitdefender Antivirus Plus',
        'family-pack': 'Bitdefender Family Pack',
        'internet-security': 'Bitdefender Internet Security',
        'mobile-security-android': 'Bitdefender Mobile Security',
        'premium-security': 'Bitdefender Premium Security',
        'total-security': 'Bitdefender Total Security',
        'antivirus-for-mac': 'Bitdefender Antivirus for Mac'
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

    def parse(self, response):
        url = urlparse(response.request.url)

        pathl = list(filter(None, url.path.split('/')))
        if not pathl and response.request.meta['redirect_urls']:
            yield {
                'URL': response.request.meta['redirect_urls'][-1],
                'Date': today,
                'Source': url.hostname,
                'Brand': 'Bitdefender',
                'Country': None,
                'Device Types': None,
                'Devices': None,
                'Product Name': 'Redirected to homepage',
                'Current Price': None,
                'Regular Price': None,
                'Term': None,
                'Currency': None
            }
            return

        country_code = url.hostname.split('.')[-1]
        if country_code == 'com':
            country_code = 'us'
        if country_code == 'uk':
            country_code = 'gb'
        country = self.countries[country_code]

        product_code = pathl[-1].rpartition('.')[0]
        product_id = response.css('#product-id::attr(value)').get()

        pricing_url = f'http://{url.hostname}/bin/' \
            f'checkout.{product_id}.{country["regionId"]}.{country["currency"]}.' \
            f'{country_code.upper()}.consumer.null.json'

        yield Request(
            pricing_url, callback=self.parse_pricing,
            cb_kwargs={
                'URL': response.request.url,
                'Date': today,
                'Source': url.hostname,
                'Brand': 'Bitdefender',
                'Country': helpers.country_codes[country_code],
                'Device Types': self.platforms[product_code],
                'Product Name': self.products[product_code]
            },
            meta={'dont_itemise_on_400s': True},
            headers={
                'domain': url.hostname,
                'accept': 'application/json,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            }

        )

    def parse_pricing(self, response, **item):
        pricing = response.json()
        currency = pricing['PricingConfigurations'][0]['DefaultCurrency']

        for price in pricing['PricingConfigurations'][0]['Prices']['Regular']:
            if price['Currency'] != currency:
                continue

            options = re.match(
                r'([a-zA-Z0-9]{,4})-(?P<devs>\d+)u-(?P<term>\d+)(?P<time_unit>[ym])',
                price['OptionCodes'][0]['Options'][0]
            )
            time_unit = options.group('time_unit')
            term = options.group('term')
            if time_unit == 'm':
                term = f'{float(term) / 12.0:.1f} year'
            else:
                term = f'{term} year'

            yield {
                'Current Price': price.get('discountedPrice'),
                'Regular Price': price['Amount'],
                'Currency': currency,
                'Devices': options.group('devs'),
                'Term': term,
                **item
            }
