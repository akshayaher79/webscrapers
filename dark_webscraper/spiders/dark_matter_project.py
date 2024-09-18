from scrapy import Spider
from datetime import datetime, timezone


class DarkMatterProjec(Spider):
    name = 'darkmatter'
    allowed_domains = [
        'dark4s5k7jw5zjgkm5wzo3zbvwpwvzi7gqo5kpvzfggtcnzexdu7gsyd.onion'
    ]

    start_urls = [
        'https://dark4s5k7jw5zjgkm5wzo3zbvwpwvzi7gqo5kpvzfggtcnzexdu7gsyd.onion'
    ]

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,
    }

    def parse(self, response):
        yield from response.follow_all(
            css='.entry-content .product-category a',
            callback=self.parse_category
        )

    def parse_category(self, response):
        yield from response.follow_all(
            css='.products .product a:first-child',
            callback=self.parse_product
        )

    def parse_product(self, response):
        title = response.css('.entry-title::text').get()
        price = response.css(
            '.entry-summary .woocommerce-Price-amount bdi::text'
        ).get()
        category = response.css('.product_meta a::text').get()
        res_time = datetime.strptime(
            str(response.headers.get('Date'), encoding='utf-8'),
            '%a, %d %b %Y %H:%M:%S %Z'
        ).astimezone(timezone.utc).isoformat()

        return {
            'content': 'General Market',
            'website_name': 'Dark Matter Project',
            'timestamp': '',
            'date_of_scrape': response.headers.get('Date'),
            'text': title.strip(),
            'url': response.request.url,
            'post_num': '',
            'extradata': {
                'Price': price,
                'Category': category.strip()
            }
        }
