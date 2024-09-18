from scrapy import Spider
from datetime import datetime, timezone


class KholChand(Spider):

    name = 'kholchan.net'
    allowed_domains = ['kohlchan.net']

    start_urls = [
        'https://kohlchan.net/a',
        'https://kohlchan.net/nvip/',
        'https://kohlchan.net/alt/',
        'https://kohlchan.net/bus/',
        'https://kohlchan.net/c/',
        'https://kohlchan.net/co/',
        'https://kohlchan.net/cyber/',
        'https://kohlchan.net/d/',
        'https://kohlchan.net/e/',
        'https://kohlchan.net/f/',
        'https://kohlchan.net/fb/',
        'https://dietchan.org/fefe/',
        'https://kohlchan.net/fit/',
        'https://kohlchan.net/foto/',
        'https://kohlchan.net/jp/',
        'https://kohlchan.net/l/',
        'https://kohlchan.net/mali/',
        'https://kohlchan.net/med/',
        'https://kohlchan.net/mu/',
        'https://kohlchan.net/n/',
        'https://kohlchan.net/ng/',
        'https://kohlchan.net/pol/',
        'https://kohlchan.net/prog/',
        'https://kohlchan.net/q/',
        'https://kohlchan.net/s/',
        'https://kohlchan.net/tu/',
        'https://kohlchan.net/tv/',
        'https://kohlchan.net/v/',
        'https://kohlchan.net/w/',
        'https://kohlchan.net/we/',
        'https://kohlchan.net/z/'
    ]
    
#   custom_settings = {
#     'CONCURRENT_REQUESTS': 1,
#       'DOWNLOAD_DELAY': 3,
#      'ITEM_PIPELINES': {
#           'DMP.pipelines.PostgresPipeline': 300
#           }
#   }

    def parse(self, response):
        yield from response.follow_all(
            css='.opHead > a.linkQuote',
            callback=self.parse_thread
        )

        next = response.css('.threadPages a#linkNext')
        if next:
            yield response.follow(
                url=next[0],
                callback=self.parse,
            )

    def parse_thread(self, response):

        res_time = datetime.strptime(
            str(response.headers.get('Date'), encoding='utf-8'),
            '%a, %d %b %Y %H:%M:%S %Z'
        ).astimezone(timezone.utc).isoformat()
        board = response.css('#labelName::text').get()

        op = response.css('.innerOP')
        subject = op.css('.labelSubject::text').get()
        username = op.css('.linkName::text').get()
        timestamp = op.css('.labelCreated::text').get()
        id = op.css('.linkQuote::text').get()
        text = op.css('.divMessage').xpath('normalize-space()').get()

        yield {
            'website_name': 'Kholchan',
            'url': response.request.url,
            'timestamp': timestamp,
            'text': text,
            'post_num': id,
            'date_of_scrap': res_time,
            'content': 'General Market',
            'extradata': {
                'board': board,
                'subject': subject,
                'username': username
            }
        }

        for reply in response.css('.postCell'):
            subject = reply.css('.labelSubject::text').get()
            username = reply.css('.linkName::text').get()
            timestamp = reply.css('.labelCreated::text').get()
            id = reply.css('.linkQuote::text').get()
            text = reply.css('.divMessage').xpath('normalize-space()').get()

            yield {
                'website_name': 'Kholchan',
                'url': response.request.url,
                'timestamp': timestamp,
                'text': text,
                'post_num': id,
                'date_of_scrap': res_time,
                'content': 'General Market',
                'extradata': {
                    'board': board,
                    'subject': subject,
                    'username': username
                }
            }
