from scrapy import Spider
from datetime import datetime, timezone


class SecretMarket(Spider):

    name = 'secretmarket'
    allowed_domains = [
        'secrn2yymnducpam.onion'
    ]

    start_urls = [
        'http://secrn2yymnducpam.onion'
    ]

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,
    }

    def parse(self, response):
        yield from response.follow_all(
            css='ul.nav li a',
            callback=self.parse_category
        )

    def parse_category(self, response):
        yield from response.follow_all(
            css='.col-lg-4 .image a',
            callback=self.parse_product
        )

        next = response.xpath('//li/a[contains(text(),">")]')

        if next:
            yield response.follow(
                url=next[0],
                callback=self.parse_category,
            )

    def parse_product(self, response):
        title = response.css('.col-sm-4 h1::text').get()
        price = response.css('.list-unstyled h2::text').get()
        description = response.css(
            '#tab-description > p:first-child::text').get()
        details = dict(
            i.xpath('normalize-space()').get().split(': ')
            for i in response.css('.col-sm-4 > ul')[0].css('li')
        )
        res_time = datetime.strptime(
            str(response.headers.get('Date'), encoding='utf-8'),
            '%a, %d %b %Y %H:%M:%S %Z'
        ).astimezone(timezone.utc).isoformat()

        yield {
                'website_name': 'Secret Market',
                'url': response.request.url,
                'timestamp': '',
                'text': title,
                'post_num': '',
                'date_of_scrap': res_time,
                'content': 'General Market',
                'extradata': {
                    'details': details,
                    'price': price,
                    'description': description
                }
        }
