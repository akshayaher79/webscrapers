from scrapy import Spider
from scrapy.http import FormRequest


class LzkBwDe(Spider):
    name = 'lzk-bw.de'
    allowed_domains = ['lzk-bw.de']
    start_urls = ['https://www.lzk-bw.de/zahnarztsuche']

    def parse(self, response):
        yield FormRequest.from_response(
            response,
            formcss='.tx-pxia-dentists > form',
            callback=self.parse_results
        )

    def parse_results(self, response):
        for entry in response.css('.panel'):
            prac = entry.css('.panel-title > a::text').get()
            address = entry.css(
                '.dentist-list__contact-block:nth-child(1) > div::text'
            ).getall()
            street = address[0]
            ZIP, city = address[-1].split(maxsplit=1)
            district = address[1] if len(address) > 2 else ''

            contact = dict(
                i.split(': ')
                for i in entry.css(
                    '.dentist-list__contact-block:nth-child(2) > div::text'
                ).getall()
            )

            email = entry.css(
                '.dentist-list__contact-block:nth-child(3) > '
                'div > a[href*=Mailto]::text'
            ).get()
            website = entry.xpath(
                './/div[contains(@class, "dentist-list__contact-block") and 3]'
                '/div/a[contains(@href, string())]/@href'
            ).get()
            for pracor in entry.css('.dentist-list__profile'):
                name, specialty = pracor.css(
                    'p > strong::text'
                ).get().strip().split(' | ')

                focus = '; '.join(
                    pracor.css(
                        '.dentist-list__practice-areas > li::text'
                    ).re('Tätigkeitsschwerpunkt: (.+)')
                )

                yield {
                    'Practice': prac,
                    'Name': name,
                    'Medical Specialist': specialty,
                    'Street': street,
                    'Postal Code': ZIP,
                    'District': district,
                    'City': city,
                    'Telephone': contact.get('Tel.'),
                    'Telefax': contact.get('Fax'),
                    'Email': email,
                    'Website': website,
                    'Focus': focus
                }

        next = response.css('a.pagination__next')
        if next:
            yield response.follow(
                url=next[0],
                callback=self.parse_results
            )
