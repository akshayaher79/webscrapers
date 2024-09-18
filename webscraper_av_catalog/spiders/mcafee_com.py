# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from scrapy_selenium import SeleniumRequest

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from shutil import which
from urllib.parse import urlparse, urljoin
from datetime import date
import re
import json

from . import helpers


today = date.today().isoformat()

class McAfeeCom(Spider):
    name = 'mcafee.com'
    allowed_domains = ['mcafee.com']

    custom_settings = {
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': which('chromedriver'),
        'SELENIUM_DRIVER_ARGUMENTS': [],

        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 800
        },
        'LOG_LEVEL': 'INFO'
    }

    def __init__(self):
        with open('Antivirus/static_data/start_urls/mcafee_com.txt') as start_urls:
            self.start_urls = list(start_urls)
        super().__init__()

    def start_requests(self):
        # This site is setting a variable digitalData on the window object with all the offers on the page.
        # This snippet of JS will copy that onto the DOM in the body element's data-items attribute.
        prelim_js = """
            var myattr = document.createAttribute('data-items');
            myattr.value = JSON.stringify(digitalData);
            document.getElementsByTagName('body')[0].setAttributeNode(myattr);
        """
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                wait_time=4,
                wait_until=EC.element_attribute_to_include((By.CLASS_NAME, 'cmp-a'), 'data-finalprice'),
                script=prelim_js,
                errback=self.handle_webdriver_timeout
            )

    products = {
        'android': 'Total Protection',
        'gaming': 'Gamer Security',
        'mcafee-total-protection': 'Total Protection',
        'mcafee-safe-connect': 'Total Protection',
        'antivirus': 'Total Protection'
    }
    platforms = {
        'android': 'PC (Windows), Mac, Android phone/tablet, iPad/iPhone',
        'mcafee-total-protection': 'PC (Windows), Mac, Android phone/tablet, iPad/iPhone',
        'gaming': 'PC (Windows)',
        'mcafee-safe-connect': 'PC (Windows), Chromebook, Android phone/tablet, iPhone/iPad',
        'antivirus': 'PC (Windows), Mac, Android phone/tablet, iPad/iPhone'
    }

    def handle_webdriver_timeout(self, failure):
        # The WebDriver times out waiting for content in 404 responses.
        if failure.check(TimeoutException):
            yield {
                'Date': today,
                'Source': 'mcafee.com',
                'Brand': 'McAfee',
                'Country': None,
                'Product Name': 'URL not reachable at this time',
                'URL': failure.request.url,
                'Devices': None,
                'Term': None,
                'Device Types': None,
                'Current Price': None,
                'Regular Price': None,
                'Currency': None
            }

    def parse(self, response):
        url = urlparse(response.request.url)
        pathl = list(filter(None, url.path.split('/')))

        country = helpers.country_codes[pathl[0].partition('-')[2]]
        product_code = pathl[-1].rpartition('.')[0]
        product = self.products[product_code]
        dev_types = self.platforms[product_code]
        
        citation = urljoin(
            f'https://{url.hostname}',
            response.css('a[data-navelement="total-protection"]::attr(href)').get()
        )
        for offer in json.loads(response.css('body::attr(data-items)').get())['offers'].values():
            price = offer.get('finalPrice')
            price = ''.join(re.findall('[0-9][0-9 .,]+', price))

            if price in ['0', '0,00', '0.00']:
                continue

            MRP = offer.get('retailPrice')
            MRP = ''.join(re.findall('[0-9][0-9 .,]+', MRP))

            devs = offer.get('productNumberOfDevices')
            if not devs:
                devs = response.xpath(
                    '//div[@class and contains(concat(" ", normalize-space(@class), " "), " card ")]'
                    '['
                        './/a['
                            '@class and contains(concat(" ", normalize-space(@class), " "), " cmp-a ") '
                            'and @data-packagecode="' + offer.get('packageCode') + '"'
                        ']'
                    ']'
                ).css(
                    '.mc__pr_device::text, '
                    'small.text-center::text, '
                    '.p-price-list > li:first-child > span::text'
                ).get(default='')

            devs = re.search('[0-9]+', devs)
            devs = devs.group() if devs else None

            currency = offer.get('currencyCode')

            yield {
                'Date': today,
                'Source': 'mcafee.com',
                'Brand': 'McAfee',
                'Country': country,
                'Product Name': product,
                'Input URL': response.request.url,
                'URL': citation,
                'Devices': devs,
                'Term': '1 year',
                'Device Types': dev_types,
                'Current Price': price,
                'Regular Price': MRP,
                'Currency': currency
            }
