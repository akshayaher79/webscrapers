from scrapy import Request, Spider
from ..items import Agent
from pkg_resources import resource_stream
from json import loads as jsonparse
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


class ZillowCom(Spider):
    """
    Searches the whole site for realtors in all areas in the US ZIP
    postal system and extracts details from their profile pages. Also
    crawls SERPs of the website's search engine whose URLs are listed
    in the start URLs file.

    Spider parameters
    =================

    start_urls_f
    ------------
    Path to a text file containing start URLs.
    """

    name = 'zillow.com'
    allowed_domains = ['zillow.com']

    custom_settings = {
        'ITEM_PIPELINES': {
            'brokerage_info_crawler.pipelines.NameCleaner': 300,
            'brokerage_info_crawler.pipelines.CityCleaner': 301,
            'brokerage_info_crawler.pipelines.NumberCleaner': 302
        }
    }

    def __init__(self, start_urls_f=None):
        if start_urls_f:
            with open(start_urls_f) as start_urls:
                self.start_urls = [url.rstrip() for url in start_urls]
        super().__init__()

    def start_requests(self):
        yield from super().start_requests()
        with resource_stream(
            'brokerage_info_crawler.static_data', 'ZIPs.txt'
        ) as zips:
            for zip_ in zips:
                zip_ = str(zip_, encoding='utf-8').rstrip()
                yield Request(
                    f'https://www.zillow.com/professionals/real-estate-agent-reviews/{zip_}'
                )

    def parse(self, response):
        yield from response.follow_all(
            css='table[aria-label="Agent\'s table"] > tbody > tr > '
                'td > a.StyledTextButton-c11n-8-50-1__sc-n1gfmh-0.jMHzWg',
            callback=self.parse_profile
        )

        nextbtn = response.css('button[rel=next].egGLJY')
        if nextbtn:
            url = urlparse(response.request.url)
            yield Request(
              urlunparse(
                url._replace(
                  query=urlencode(
                    {'page': int(*(parse_qs(url.query).get('page') or [])) + 1}
                  )))
            )

    def parse_profile(self, response):
        data = jsonparse(
            response.css('#__NEXT_DATA__::text').get(
            ).replace(r'\"', "'").replace('\\', '\\\\')
        )['props']['pageProps']
        agent = Agent()

        # Identity and contact details
        agent['DP_URL'] = data['profileDisplay']['contactCard']['proilePhotoSrc']
        agent['URL'] = response.request.url

        proinfo = {
            item['term']: item
            for item in data['professionalInformation']
        }

        # Office details
        agent['brand'], agent['street'], region = proinfo['Broker address']['lines']
        agent['city'], state_zip = region.split(', ')
        agent['state'], agent['ZIP'] = state_zip.split()

        agent['name'] = data['displayUser']['name']
        agent['title'] = data['about']['title']

        agent['phone'] = proinfo['Cell phone']['description']
        agent['phone_alt'] = proinfo['Broker phone']['description']
        agent['work_tel'] = proinfo['Office phone']['description']

        # Social media IDs and pages
        for link in proinfo['Websites']['links']:
            agent[link['text'].lower()] = link['url']

        # Practice details
        agent['turf'] = '; '.join(data['about']['serviceAreas'])
        agent['skills'] = '; '.join(data['about']['specialties'])
        agent['firstyear'] = data['about']['yearsExperience']

        return agent
