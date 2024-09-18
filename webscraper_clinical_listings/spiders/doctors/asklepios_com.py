from scrapy import Spider


class AsklepiosCom(Spider):
    name = 'asklepios.com'
    allowed_domains = ['asklepios.com']

    start_urls = [
        'https://www.asklepios.com/konzern/standorte'
        '/aerztesuche~mgnlArea=container,result~?&start=' + str(i)
        for i in range(0, 2040, 20)
    ]

    def parse(self, response):
        yield from response.follow_all(
            css='.b-doctor-result-teaser .link[href*="arztprofil"]',
            callback=self.parse_profile
        )

    def parse_profile(self, response):
        name = response.css('.b-profile-doc-info > header > h1::text').get()
        func = response.css('.b-profile-doc-info > header > h2::text').get()

        clinic_name = response.css('.logo__name::text').get()
        departments = response.css('.departments li > a::text').getall()

        spec = response.css(
            '.b-profile-doc-info .text > p::text'
        ).getall()

        tel = response.css('.b-contact-infos > li.tel > a::text').get()

        fax = response.css('.b-contact-infos > li.fax::text').get()

        return {
            'URL': response.request.url,
            'Name': name,
            'Function': func,
            'Hospital Name': clinic_name,
            'Departments': '; '.join(departments),
            'Specilaisations': '; '.join(spec),
            'Telephone': tel,
            'Fax': fax
        }
