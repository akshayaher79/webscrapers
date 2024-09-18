from scrapy import Spider
from scrapy.http import FormRequest
from ..helpers import parse_desc_list


class ArztsucheBwDe(Spider):

    name = 'arztsuche-bw.de'
    allowed_domains = ['arztsuche-bw.de']
    start_urls = [
        'https://www.arztsuche-bw.de'
        '/index.php?suchen=0&expertensuche=1'
    ]

    custom_settings = {
        'FEED_EXPORT_FIELDS': [
            'Name', 'Website', 'E-Mail', 'Practice', 'Street', 'ZIP-City',
            'Sprechstundenzeiten', 'Offene Sprechstunden', 'Telefon', 'Telefax',
            'Facharzt / Fachgebiet', 'Hausarzt / Fachgebiet', 'DMP',
            'Schlüsselnummern', 'Fremdsprachen', 'Praxisart', 'Rechtsstatus',
            'Zusatzbezeichnungen', 'Genehmigungen', 'Sonstige Praxismerkmale',
            'Weitere Ärzte/Psychotherapeuten der Praxis'
        ]
    }

    def parse(self, response):
        yield FormRequest.from_response(
            response,
            formid='kvbw_suche',
            formdata={
                'geschlecht': 'm'
            },
            callback=self.parse_results
        )
        yield FormRequest.from_response(
            response,
            formid='kvbw_suche',
            formdata={
                'geschlecht': 'w'
            },
            callback=self.parse_results
        )

    def parse_results(self, response):
        for entry in response.css('.resultrow > dl'):
            # Top row, left column
            name = entry.css(
                'dd.name > dl > dt:first-child::text'
            ).get()

            hours = {}
            for table in entry.css('.termintabelle > tbody'):
                caption = table.xpath(
                    './parent::dd/preceding-sibling::dt[1]'
                    '/text()[normalize-space()]'
                ).get().strip()
                hours[caption] = ' | '.join(
                    tr.xpath('string()').get() for tr in table.css('tr')
                )

            # Top row, middle column
            qual = {}
            for dl in entry.css('dd.qualifikation > dl > dl.bulletlist'):
                qual.update({
                	k.partition(':')[0].strip(): '; '.join(v) for k, v in
                	parse_desc_list(dl).items()
                })

            # Bottom row
            details = {}
            for dl in entry.css('.slidecontent > .column > dl'):
                details.update({
                	k.partition(':')[0].strip(): '; '.join(v) for k, v in
                	parse_desc_list(dl).items()
                })

            # Top row, right column
            address = entry.css('dd.adresse .anschrift-arzt::text').getall()
            contact = entry.xpath(
                './/dd[@class="adresse"]/dl'
                '/dt[contains(string(), "Kontaktdaten")]'
                '/following-sibling::dd/text()'
            ).getall()
            address_contact = dict(
                zip(
                    ['Practice', 'Street', 'ZIP-City'],
                    address[0:3]
                )
            )
            for i in address[3:] + contact:
                if ': ' in i.strip():
                    k, v = i.split(': ', maxsplit=1)
                    address_contact[k] = v

            web = entry.css(
                'dd.adresse > dl > dd > '
                'a[title="Homepage aufrufen"]::attr(href)'
            ).get()
            email = ' '.join(
                entry.css('.obfuscatedEmail::attr(href)').getall()
            )

            yield {
                'Name': name,
                'E-Mail': email,
                'Website': web,
                **address_contact,
                **details,
                **qual,
                **hours
            }

        yield FormRequest.from_response(
            response,
            formxpath='//div[@class="pagination"]'
                      '//button[contains(@class, "next-button")]'
                      '/parent::form',
            callback=self.parse_results
        )
