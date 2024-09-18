from scrapy import (Request, Spider)
from scrapy.http import FormRequest
from pkg_resources import resource_filename
import csv
import re


class KvhessenDe(Spider):

    name = 'kvhessen.de'
    allowed_domains = ['arztsuchehessen.de']

    # Logs into website in multiple sessions for every ZIP and city.
    def start_requests(self):
        with open(
            resource_filename('doc_info_crawler.static_data', 'ZIPs/HS.csv'),
            newline=''
        ) as zipsf:
            zips = csv.reader(zipsf)
            for zip_, city in zips:
                yield Request(
                    url='https://arztsuchehessen.de/arztsuche/arztsuche.php',
                    # Separate cookie jar per ZIP
                    meta={'cookiejar': zip_},
                    cb_kwargs={'plz': zip_, 'ort': city},
                    dont_filter=True
                )

    # Fills up the form at the start URL.
    def parse(self, response, **query):
        yield FormRequest.from_response(
            response, callback=self.parse_result_page,
            formdata={
                # Force type of page through query
                'page': 'ergebnisliste',
                'plz': query['plz'],
                # 'ort': query['ort']
            },
            meta={
                'cookiejar': response.meta['cookiejar']
            }
        )

    def parse_result_page(self, response):
        yield from response.follow_all(
            css='td:first-child a[title="zur Karteikarte"]',
            callback=self.parse_profile_page,
            meta={
                'cookiejar': response.meta['cookiejar']
            }
        )

        next = response.css('a[title="weiter"]::attr(href)').get()
        if next:
            yield response.follow(
                next, callback=self.parse_result_page,
                dont_filter=True,
                meta={
                    'cookiejar': response.meta['cookiejar']
                }
            )

    day = re.compile(r'(Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag)')
    timings = re.compile(r'\s*von (\d\d:\d\d) Uhr bis (\d\d:\d\d) Uhr')

    def parse_profile_page(self, response):
        name = response.css('div.Arzt::text').get().strip()

        address = response.xpath(
            '//div[contains(text(), "Adresse:")]'
            '/following-sibling::div[1]/text()'
        ).getall()
        street = address[0].strip()
        ZIP, city = address[1].strip().split(' ', maxsplit=1)

        tel = response.xpath(
            '//div[contains(text(), "Telefon:")]'
            '/following-sibling::div[1]/text()'
        ).getall()
        tel = [i.strip() for i in tel]

        fax = response.xpath(
            '//div[contains(text(), "Telefax:")]'
            '/following-sibling::div[1]/text()'
        ).getall()
        fax = [i.strip() for i in fax]

        email = response.css('a.maillink::attr(href)').get(default='')
        email = email.partition(':')[2]

        hours = []
        for period in response.xpath(
            '//div[contains(text(), "Sprechstunde:")]'
            '/following-sibling::div[1]'
            '/div[@class="Sprechzeit"]'
        ):

            day = period.re_first(self.day)
            timings = period.re(self.timings)
            timings = zip(timings[::2], timings[1::2])
            hours.append((day, [f'{s}-{e}' for s, e in timings]))

        # Praxismerkmale field on the profile page
        ofc_feat = response.xpath(
            '//div[contains(text(), "Praxismerkmale")]'
            '/following-sibling::div[1]/text()'
        ).getall()
        ofc_feat = [i.strip() for i in ofc_feat]

        # Fachgebiet field on the profile page
        focus = response.xpath(
            '//div[contains(text(), "Fachgebiet:")]'
            '/following-sibling::div[1]/text()'
        ).getall()
        focus = [i.strip() for i in focus]

        status = response.xpath(
            '//div[contains(text(), "Status:")]'
            '/following-sibling::div[1]/text()'
        ).getall()
        status = [i.strip() for i in status]

        # Weitere Merkmale field on the profile page
        add_feat = response.xpath(
            '//div[contains(text(), "Weitere Merkmale:")]'
            '/following-sibling::div[1]/text()'
        ).getall()
        add_feat = [i.strip() for i in add_feat]

        # Fremdsprachen field on the profile page
        langs = response.xpath(
            '//div[contains(text(), "Fremdsprachen:")]'
            '/following-sibling::div[1]/text()'
        ).getall()
        langs = [i.strip() for i in langs]

        coworkers = response.css('div.mitarbeiter a::attr(href)').getall()

        return {
            'Profile URL': response.request.url,
            'Name': name,
            'Telephone': '; '.join(tel),
            'Fax': '; '.join(fax),
            'Email': email,
            'Street': street,
            'City': city,
            'ZIP': ZIP,
            'Status': '; '.join(status),
            'Foreign Languages': '; '.join(langs),
            'Focus': '; '.join(focus),
            'Office Hours': ' | '.join(f'{d} {", ".join(t)}' for d, t in hours),
            'Office Features': '; '.join(ofc_feat),
            'Other Features': '; '.join(add_feat),
            'Related Profile URLs': ' '.join(coworkers)
        }
