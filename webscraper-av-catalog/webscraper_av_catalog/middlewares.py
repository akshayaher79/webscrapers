# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

from datetime import date
from urllib.parse import urlparse

from .spiders import helpers


today = date.today().isoformat()


class Http400sResponse(Exception):
    """A 400-something HTTP response was received."""

    def __init__(self, response, *args, **kwargs):
        self.response = response
        super().__init__(*args, **kwargs)


class Http400sMiddleware():
    """Spider middleware to itemise responses with a 400-499 HTTP status in the item feed."""

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_spider_input(self, response, spider):
        if response.request.meta.get('dont_itemise_on_400s'):
            return

        if response.status >= 400 and response.status <= 499:
            raise Http400sResponse(response)

    brands = {
        'kaspersky.com': 'Kaspersky',
        'avast.com': 'Avast',
        'avg.com': 'AVG',
        'eset.com': 'ESET',
        'trendmicro.com': 'Trend Micro',
        'k7computing.com': 'K7',
        'webroot.com': 'Webroot',
        'bitdefender.com': 'Bitdefender',
        'bitdefender1': 'Bitdefender',
        'bitdefender2': 'Bitdefender',
        'bitdefender.*': 'Bitdefender',
        'mcafee.com': 'McAfee',
        'norton.com': 'Norton'
    }

    def process_spider_exception(self, response, exception, spider):
        if response.request.meta.get('dont_itemise_on_400s'):
            return

        if isinstance(exception, Http400sResponse):
            url = urlparse(response.request.url)
            return [
                {
                    'Date': today,
                    'Source': url.hostname,
                    'Brand': self.brands.get(spider.name),
                    'Country': '',
                    'Product Name': 'URL not reachable at this time',
                    'URL': response.request.url,
                    'Devices': '',
                    'Device Types': '',
                    'Term': '',
                    'Current Price': '',
                    'Regular Price': '',
                    'Currency': ''
                }
            ]


class AntivirusDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
