from scrapy import Spider
from scrapy.http import FormRequest
from pkg_resources import resource_filename


class KzvnDe(Spider):

    name = 'kzvn.de'
    allowed_domains = ['kzvn.de']
    start_urls = ['https://kzvn.de/patienten/zahnarztsuche.html']

    custom_settings = {
        'FEED_EXPORT_FIELDS': [
            'Practice', 'Name', 'Street', 'ZIP', 'City',
            'Tel.', 'Fax', 'E-Mail', 'Website'
        ]
    }

    def parse(self, response):
        with open(
            resource_filename('doc_info_crawler.static_data', 'ZIPs/NI.txt')
        ) as zips:
            for zip_ in zips:
                yield FormRequest.from_response(
                    response,
                    formcss='#print2 form[name="reset"]',
                    formdata={
                        'plz': zip_.strip(),
                        'umkreis': 5
                    },
                    callback=self.parse_results
                )

    def parse_results(self, response):
        for entry in response.css('.zasuche'):
            prac = entry.css('b:first-child::text').get()

            address = entry.css('::text').get()
            street, ZIP_city = address.split(', ', maxsplit=1)
            ZIP, city = ZIP_city.split(maxsplit=1)

            for name in prac[8:].split(','):
                yield {
                    'Practice': prac,
                    'Name': name,
                    'Street': street,
                    'ZIP': ZIP,
                    'City': city,
                    **dict(
                        i.xpath('string()').get().split(': ', maxsplit=1)
                        for i in entry.css('i')
                    )
                }
        next = response.xpath('//div[@id="print2"]//a[string()="vor"]')
        if next:
            yield response.follow(
                url=next[0],
                callback=self.parse_results
            )
