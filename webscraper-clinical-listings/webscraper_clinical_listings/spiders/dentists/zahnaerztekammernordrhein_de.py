import scrapy
from scrapy import Spider
from scrapy.http import FormRequest
from pkg_resources import resource_filename


class ZahnaerztekammernordrheinDe(Spider):
    name = 'zahnaerztekammernordrhein.de'
    allowed_domains = ['zahnaerztekammernordrhein.de']
    start_urls = [
        'https://www.zahnaerztekammernordrhein.de'
        '/fuer-die-praxis-fortbildung/'
    ]

    def parse(self, response):
        action = response.urljoin(
            response.css(
                '#c26 > .tx-ddfzahnaerzte > '
                '.zahnarzt_filter.filterbox > form::attr("data-sucheuri")'
            ).get()
        )

        with open(
            resource_filename('doc_info_crawler.static_data', 'ZIPs/NO.txt')
        ) as zips:
            for zip_ in zips:
                yield FormRequest.from_response(
                    response,
                    url=action,
                    method='POST',
                    formcss='#c26 > .tx-ddfzahnaerzte > '
                            '.zahnarzt_filter.filterbox > form',
                    formdata={
                        'tx_ddfzahnaerzte_ddfzahnarztsuche[filter_plz]':
                            zip_.strip()
                    },
                    callback=self.parse_results
                )

    def parse_results(self, response):
        for entry in response.css('div.singleZahnarzt'):
            name = entry.css('.name::text').get().strip()
            spec = entry.css('.facharzt::text').get(default='').strip()
            focus = entry.css('.tsp::text').get(default='').strip()
            phone = entry.css('.phone::text').get(default='').strip()
            fax = entry.css('.fax::text').get(default='').strip()
            website = entry.css('.web > a::text').get(default='').strip()
            email = entry.css('.email > a::text').get(default='').strip()
            street = entry.css(
                '.adress > .street::text'
            ).get(default='').strip()
            ZIP, city = entry.css(
                '.adress > .town::text'
            ).get(default='- -').split(maxsplit=1)

            yield {
                'Name': name,
                'Specialty': spec,
                'Focused Activities': focus,
                'Phone': phone,
                'Fax': fax,
                'Website': website,
                'Email': email,
                'Street': street,
                'ZIP': ZIP,
                'City': city
            }
