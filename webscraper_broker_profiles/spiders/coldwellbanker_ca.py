from scrapy import Spider
from ..items import Agent


class ColdwellBankerCa(Spider):

    name = 'coldwellbanker.ca'
    allowed_domains = ['coldwellbanker.ca']

    start_urls = ['https://www.coldwellbanker.ca/agents/ca']
    custom_settings = {
        'ITEM_PIPELINES': {
            'brokerage_info_crawler.pipelines.StateNameEncoder': 302,
            'brokerage_info_crawler.pipelines.NumberCleaner': 303,
            'brokerage_info_crawler.pipelines.NameCleaner': 304
        },

        'DOWNLOAD_DELAY': 10,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1
    }

    def parse(self, response):
        yield from response.follow_all(
            css='.agent-view-listing > a',
            callback=self.parse_profile
        )

        next = response.css('.pagination > .next-page > a')
        if next:
            yield response.follow(
                url=next[0],
                callback=self.parse
            )

    def parse_profile(self, response):
        agent = Agent()

        agent['URL'] = response.request.url
        agent['DP_URL'] = response.css('.profile-image > img::attr(src)').get()

        agent['name'] = response.css('.agent-name::text').get()
        agent['title'] = response.css('.job-title::text').get()
        agent['creds'] = '; '.join(
            response.css(
                'agent-badge agent-badge-image::attr(alt)'
            ).getall()
        )

        agent['phone'] = response.xpath(
            '//address[@class="agent-contacts"]'
            '/p[contains(text(), "Mobile:")]/span/text()'
        ).get()

        agent['work_tel'] = response.xpath(
            '//address[@class="agent-contacts"]'
            '/p[contains(text(), "Office:")]/span/text()'
        ).get()

        # agent['fax'] = response.xpath(
        #     '//address[@class="agent-contacts"]'
        #     '/p[contains(text(), "Fax:")]/span/text()'
        # ).get()

        agent['website'] = response.xpath(
            '//address[@class="agent-contacts"]'
            '/p[contains(text(), "Web:")]/a/@href'
        ).get()

        agent['email'] = response.xpath(
            '//div[@class="agent-contacts-actions"]'
            '//a[contains(i/@class, "fa-envelope-o")]/@href'
        ).get(default='').partition(':')[2]

        agent['facebook'] = response.xpath(
            '//div[@class="agent-contacts-actions"]'
            '/a[contains(i/@class, "fa-facebook")]/@href'
        ).get()
        agent['linkedin'] = response.xpath(
            '//div[@class="agent-contacts-actions"]'
            '//a[contains(i/@class, "fa-linkedin")]/@href'
        ).get()
        agent['twitter'] = response.xpath(
            '//div[@class="agent-contacts-actions"]'
            '//a[contains(i/@class, "fa-twitter")]/@href'
        ).get()

        agent['brand'] = response.css('address.agent-office > a > span::text').get()
        agent['street'], region = response.css(
            'address.agent-office > span > span::text'
        ).getall()
        region, agent['ZIP'] = region.rsplit(maxsplit=1)
        agent['city'], agent['state'] = region.split(',')

        agent['lang'] = '; '.join(
            response.css('.agent-languages > div > ul > li::text').getall()
        )

        agent['skills'] = '; '.join(
            response.xpath(
                '//div[@class="agent-section"]'
                '/h2[contains(string(), "Specialties") '
                 'or contains(string(), "Specialty Markets")]'
                '/following-sibling::div/ul/li/text()'
            ).getall()
        )

        agent['creds'] = '; '.join(
            response.xpath(
                '//div[@class="agent-section"]'
                '/h2[contains(string(), "Credentials")]'
                '/following-sibling::div/ul/li/text()'
            ).getall()
        )

        return agent
