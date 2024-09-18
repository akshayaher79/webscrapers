from scrapy import Spider
from ..items import Agent


class ColdwellBanker(Spider):

    name = 'coldwellbanker.com'
    allowed_domains = ['coldwellbanker.com']

    start_urls = ['https://www.coldwellbanker.com/real-estate-agents']
    custom_settings = {
        'ITEM_PIPELINES': {
            'brokerage_info_crawler.pipelines.StateNameEncoder': 302,
            'brokerage_info_crawler.pipelines.NumberCleaner': 303
        }
    }

    def parse(self, response):
        yield from response.follow_all(
            css='.areaListCol > span > a',  # State-wise brokerage lists
            callback=self.parse_state
        )

    def parse_state(self, response):
        yield from response.follow_all(
            css='.l-grid.pb-20 > ul > li:first-child > a',  # Brokerage pages
            callback=self.parse_brokerage
        )

    def parse_brokerage(self, response):
        yield from response.follow_all(
            css='.pod__office > h3 > a',  # Office pages, near the bottom
            callback=self.parse_office
        )

    def parse_office(self, response):
        yield from response.follow_all(
            css='.results-row > a',
            callback=self.parse_profile
        )

    def parse_profile(self, response):
        agent = Agent()

        agent['URL'] = response.request.url
        agent['DP_URL'] = response.css(
            '.media img[itemprop=image]::attr(src)'
        ).get()

        agent['name'] = response.css(
            '.agent-heading > h1[itemprop=name]::text'
        ).get()
        agent['phone'] = response.css(
            '.agent-info-cont__agent-phone > a::text'
        ).get()

        agent['creds'] = '; '.join(
            response.css(
                '.agent-info-cont__agent-icons img::attr(alt)'
            ).getall()
        )

        address = response.css(
            '.broker-ftr > .f-left > .media > .media__content'
        )
        company = address.css(
            '.mls-company-name::text'
        ).get()
        agent['brand'] = company[:15]

        addrlines = address.xpath('text()[normalize-space()]').getall()
        agent['street'] = addrlines[0].strip()
        agent['city'], state_ZIP = addrlines[1].strip().split(',', maxsplit=1)
        agent['state'], agent['ZIP'] = state_ZIP.strip().split(' ', maxsplit=1)
        agent['branch'] = f'{company[16:]} {agent["city"]} Office'

        agent['work_tel'] = address.css(
            '.f-icon-phone + strong::text'
        ).get(default='').strip()

        agent['rating'] = response.css(
            '#star-ratings > .review-text > span::text'
        ).get()

        agent['turf'] = '; '.join(
            response.css('#all-areas-list > li > a::text').getall()
        )

        agent['lang'] = '; '.join(
            response.xpath(
                '//div[contains(@class, "pod")]'
                '/h2[contains(string(), "I Speak")]'
                '/following-sibling::ul/li/text()'
            ).getall()
        )

        agent['facebook'] = response.css(
            '.agent-social a.fm-fb::attr(href)'
        ).get()
        agent['linkedin'] = response.css(
            '.agent-social a.fm-li::attr(href)'
        ).get()
        agent['instagram'] = response.css(
            '.agent-social a.fm-ig::attr(href)'
        ).get()
        agent['twitter'] = response.css(
            '.agent-social a.fm-t::attr(href)'
        ).get()
        agent['yelp'] = response.css('.agent-social a.fm-y::attr(href)').get()

        return agent
