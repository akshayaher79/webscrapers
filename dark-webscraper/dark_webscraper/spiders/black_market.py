from scrapy import Spider


class BlackMarket(Spider):

    name = 'blackmarket'
    allowed_domains = [
        'weapon5dj7fwz2zaqa22fqeaqrauclim5kfvecegphrvxeywxoa3wuid.onion'
    ]

    start_urls = [
        'http://weapon5dj7fwz2zaqa22fqeaqrauclim5kfvecegphrvxeywxoa3wuid.onion/shop.php'
    ]

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,
#        'ITEM_PIPELINES': {
#            'DMP.pipelines.PostgresPipeline': 300
#        }
    }

    def parse(self, response):
        entries = response.css('.one-third')
        for entry in entries:
            title = entry.css('h3::text').get()
            text = entry.css('p::text').getall()
            blackprice = entry.css('div > span:nth-child(3)::text').get()
            whiteprice = entry.css('p > strong:last-child::text').get()

        return {
            'content': 'General Market',
            'website_name': 'Black Market',
            'timestamp' : '',
            'date_of_scrape' : response.headers.get('Date'),
            'text' : ' | '.join(text),
            'url': response.request.url,
            'post_num' : '',
            'extradata': {
                'title': title,
                'WhitePrice': whiteprice,
                'BlackPrice': blackprice
            }
        }
