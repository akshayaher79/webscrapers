from scrapy import Spider
from ..items import Agent


class LicenseeIo(Spider):
    name = 'licensee.io'
    allowed_domains = ['licensee.io']
    start_urls = ['https://licensee.io/']

    def parse(self, response):
        yield from response.follow_all(
            css='a.blue-text.list-group-item',
            callback=self.parse_region
        )

    def parse_region(self, response):
        yield from response.follow_all(
            css='.row > .col-md-3 > .card > .card-body > a[href*="broker"], '
                '.row > .col-md-3 > .card > .card-body > a[href*="agent"]',
            callback=self.parse_list
        )

    def parse_list(self, response):
        yield from response.follow_all(
            css='.mydiv > h4 > a',
            callback=self.parse_profile
        )

    def parse_profile(self, response):
        agent = Agent()

        fields = dict(
            (
             tr.xpath('normalize-space(th)').get(),
             tr.xpath('normalize-space(td)').get()
            ) for tr in response.xpath(
                '//table[tr/th/following-sibling::td]/tr'
            )
        )

        agent['URL'] = response.request.url

        if 'Name' in fields:
            agent['name'] = fields['Name']
        else:
            agent['name'] = fields.get('Legal Name')

        agent['title'] = fields.get('Credentials')
        agent['license'] = fields.get('License Number')

        agent['phone'] = fields.get('Phone Number')
        agent['work_tel'] = fields.get('Employer Contact Number')
        agent['email'] = fields.get('Email Address')

        if 'Company Name' in fields:
            agent['brand'] = fields['Company Name']
        elif 'Employer DBA Name' in fields:
            agent['brand'] = fields['Employer DBA Name']
        else:
            agent['brand'] = fields.get('Employer Legal Name')

        address = response.xpath(
            '//i[contains(@class, "fa-map-marker")]/following-sibling::text()'
        ).get().rsplit(', ', maxsplit=3)
        if len(address) < 4:
             address[:0] = [None] * (4 - len(address))
        agent['street'], agent['city'], agent['state'], agent['ZIP'] = address

        return agent
