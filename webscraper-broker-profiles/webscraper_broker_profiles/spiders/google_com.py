from scrapy import Spider
from scrapy.spiderloader import SpiderLoader
from scrapy.linkextractors import LinkExtractor
from scrapy_selenium import SeleniumRequest
from shutil import which
from time import sleep


class GoogleCom(Spider):
    """
    Scrapes leads to given domains and the package's available spiders'
    domains from Google SERPs. Accepts a list of search queries in a file
    as input.

    Spider parameters
    =================

    queriesf (mandatory)
    --------------------
    Path to a text file listing a search query per line.

    seek_domains (optional)
    -----------------------
    Additional domains apart from the package spiders' domains whose links the
    spider should seek in search results. The spider always seeks links to
    all domains assigned to the spiders in the project. Quote the domain list
    argument in the command line and use spaces as separators.
    """

    name = 'google.com'
    allowed_domains = ['google.com']
    custom_settings = {
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': which('chromedriver'),
        'SELENIUM_DRIVER_ARGUMENTS': [],

        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 800
        },

        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 30
    }

    def __init__(self, queriesf, seek_domains='', *args, **kwargs):
        self.queriesf = queriesf
        self.seek_domains = seek_domains.split()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)

        seek_domains = []
        spiderloader = SpiderLoader(crawler.settings)
        spidernames = spiderloader.list()
        spidernames.remove(spider.name)
        for spidername in spidernames:
            seek_domains.extend(
                spiderloader.load(spidername).allowed_domains
            )
        seek_domains += spider.seek_domains
        spider.linkextractor = LinkExtractor(
            allow_domains=seek_domains,
            restrict_css='#rso'
        )

        return spider

    def start_requests(self):
        with open(self.queriesf) as queries:
            for q in queries:
                yield SeleniumRequest(
                    url=f'https://google.com/search?q={q.rstrip()}',
                    wait_time=20
                )
                sleep(10)

    def parse(self, response):
        for link in self.linkextractor.extract_links(response):
            yield {
                'URL': link.url,
                'text': link.text
            }
