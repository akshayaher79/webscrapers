from scrapy import Spider
from urllib.parse import urlparse
from os.path import basename

class TextBinNet(Spider):
    name = 'textbin.net'
    allowed_domains = ['textbin.net']
    start_urls = ['https://textbin.net/trending']

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,
    #     'ITEM_PIPELINES': {
    # #         'DMP.pipelines.PostgresPipeline': 300
    # #     }
    }

    def parse(self, response):
        yield from response.follow_all(
            css='.card.p-1 .list-group-item > a',
            callback=self.parse_paste
        )

    def parse_paste(self, response):
        date = response.css('.media-body i.fa-calendar').xpath(
            'following-sibling::text()'
        ).get(default='').strip()
        post_id = basename(urlparse(response.request.url).path)

        title = response.css('.media-body > h5::text').get()
        format = response.css(
            '#printarea > .card-header > .badge::text'
        ).get(default='').strip()
        description = response.xpath(
            '//div[@class="card-header" and string()="Description"]'
            '/following-sibling::div/p/text()'
        ).get()

        item = {
            'url': response.request.url,
            'content': 'General Market',
            'website_name': 'Textbin.net',
            'timestamp': date,
            'post_num': post_id,
            'extradata': {
                'title': title.strip(),
                'format': format,
                'description': description.strip()
            }
        }

        return response.follow(
            url=response.css('.pull-right > a:nth-child(3)')[0],
            callback=self.parse_raw_data,
            cb_kwargs=item
        )

    def parse_raw_data(self, response, **item):
            item['text'] = response.text
            item['date_of_scraping'] = response.headers.get('Date'),
            return item
