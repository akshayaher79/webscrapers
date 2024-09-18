from scrapy import (Spider, Request)


class ZahnaerzteHhDe(Spider):
    name = 'zahnaerzte-hh.de'
    allowed_domains = ['zahnaerzte-hh.de']
    start_urls = [
        'http://zahnaerzte-hh.de/zahnaerzte-portal/zahnaerzte/zahnarztsuche/'
    ]

    def parse(self, response):
        from json import loads

        data = loads(
            response.css(
                '[data-ractive=filter]::attr(data-filter-data)'
            ).get()
        )
        for entry in data:
            yield Request(
                url=response.urljoin(entry['detailLink']),
                callback=self.parse_profile,
                cb_kwargs=entry
            )

    def parse_profile(self, response, **entry):
        cols = response.css('#searchresults > .row:nth-child(2) > .col-sm-6')

        if cols:
            activities_focus = '; '.join(
                cols[0].xpath(
                    './/h3[contains(string(), "Tätigkeitsschwerpunkte")]'
                    '/following-sibling::ul[1]/li/text()[normalize-space()]'
                ).getall()
            )
            activities_services = '; '.join(
                cols[0].xpath(
                    './/h3[contains(string(), "Leistungen")]'
                    '/following-sibling::ul[1]/li/text()[normalize-space()]'
                ).getall()
            )
            activities_office = '; '.join(
                cols[0].xpath(
                    './/h3[contains(string(), "Praxiseigenschaften")]'
                    '/following-sibling::ul[1]/li/text()[normalize-space()]'
                ).getall()
            )
            specialty = '; '.join(
                cols[0].xpath(
                    './/h3[contains(string(), "Berufsbezeichnung")]'
                    '/following-sibling::ul[1]/li/text()[normalize-space()]'
                ).getall()
            )
        else:
            activities_focus = activities_office = activities_services = \
                specialty = None

        # Office rosters
        if cols[1:]:
            employees = '; '.join(
                i.strip() for i in
                cols[1].xpath(
                    './/h3[contains(string(), "Angestellte Zahnärzte")]'
                    '/following-sibling::ul[1]/li/a/text()[normalize-space()]'
                ).getall()
            )
            owners = '; '.join(
                i.strip() for i in
                cols[1].xpath(
                    './/h3[contains(string(), "Weitere Inhaber")]'
                    '/following-sibling::ul[1]/li/a/text()[normalize-space()]'
                ).getall()
            )
        else:
            employees = owners = None

        yield {
            'BAG mit': entry['title'],
            'Name': entry['label'],
            'Medical Specialist': specialty,
            'Street': entry['street'],
            'Postal Code': entry['zip'],
            'City': entry['city'],
            'Practice Form': 'MVZ' if 'MVZ' in entry['title'] else '',
            'Telephone': entry['phone'],
            'Website': entry['internet'],
            'Activities Focus': activities_focus,
            'Activities Service': activities_services,
            'activities Office': activities_office,
            'Post': '' if entry['owner'] else 'angestellt',
            'Employees': employees,
            'Owners': owners,
        }
