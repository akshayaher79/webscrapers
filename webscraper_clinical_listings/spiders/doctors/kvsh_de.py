from scrapy import (Request, Spider)
from scrapy.http import FormRequest
from pkg_resources import resource_filename
import csv
import re


class KvshDe(Spider):

    name = 'kvsh.de'
    allowed_domains = ['arztsuche.kvsh.de']

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1
    }

    # Logs into website in multiple sessions for every ZIP and city.
    def start_requests(self):
        zipsfp = resource_filename(
            'doc_info_crawler.static_data', 'ZIPs/SH.csv')
        with open(zipsfp, newline='') as zipsf:
            zips = set(z for z, c in csv.reader(zipsf))

        for zip_ in zips:
            yield Request(
                url='https://arztsuche.kvsh.de/',
                # Separate cookie jar per ZIP
                meta={'proxy': 'localhost:24001', 'cookiejar': zip_},
                cb_kwargs={'ZIP': zip_},
                dont_filter=True
            )

    # Fills up the form at the start URL so the server initiates a search
    # and caches the results in the session.
    def parse(self, response, **query):
        self.logger.debug(
            f'Submiting query in session {response.meta["cookiejar"]}'
        )

        return FormRequest.from_response(
            response, callback=self.parse_result_page,
            formdata={
                'form:ausgewaehlterOrt_input': query['ZIP'],
                'form:ausgewaehlterOrt_hinput': query['ZIP'],
            },
            meta={
                'proxy': 'localhost:24001',
                'cookiejar': response.meta['cookiejar']
            }
        )

    # Retrieves first entry from the server cache. Crawling subsequent
    # entries proceeds in successive pasre callbacks if they are accurate hits.
    def parse_result_page(self, response):
        self.logger.debug(
            f'Commencing crawling in session {response.meta["cookiejar"]}'
        )

        jsf_viewstate = response.css(
            '#j_id__v_0\\:javax\\.faces\\.ViewState\\:1::attr(value)'
        ).get()

        return FormRequest(
            url='https://arztsuche.kvsh.de/suche.do',
            headers={'Faces-Request': 'partial/ajax'},
            formdata={
                'javax.faces.partial.ajax': 'true',
                'javax.faces.source': 'form:arztErgebnis:0:j_id_45',
                'javax.faces.partial.execute': '@all',
                'javax.faces.partial.render':
                    'form:suchergebnis+form:suchEingabe',
                'form:arztErgebnis:0:j_id_45': 'form:arztErgebnis:0:j_id_45',
                'form:ausgewaehlterArzt_input': '',
                'form:ausgewaehlterArzt_hinput': '',
                'form:ausgewaehlterOrt_input': response.meta['cookiejar'],
                'form:ausgewaehlterOrt_hinput': response.meta['cookiejar'],
                'form:ausgewaehltesFachgebiet_input': '-+egal+-',
                'form_SUBMIT': '1',
                'javax.faces.ViewState': jsf_viewstate
            },
            meta={
                'proxy': 'localhost:24001',
                'cookiejar': response.meta['cookiejar'],
            },
            callback=self.parse_profile_data,
            cb_kwargs={'ent_i': 0}
        )

    tel = re.compile(r'Telefon: (\S*)')
    fax = re.compile(r'Fax: (\S*)')
    pracform = re.compile(
        r'\bMVZ\b|\bZMV\b|' \
        r'\b(Überörtl\.? )?Berufsausübungsgemeinschaft\b|Ü?BAG'
    )

    def parse_profile_data(self, response, ent_i):
        address = response.xpath(
            '//div[@id="form:j_id_4a_content"]' \
            '/text()[preceding-sibling::b/text()="Anschrift"]'
        ).getall()
        practice = address[0].strip()
        street = address[1].strip()
        ZIP, city = address[2].strip().split(' ', maxsplit=1)
        pracform = self.pracform.search(practice)
        if pracform:
            pracform = pracform.group()

        # Approximate hit for queried ZIP, terminate crawling in this session.
        if ZIP != response.meta['cookiejar']:
            return

        title = response.xpath(
            '//div[@id="form:j_id_4a_content"]'
            '/text()[following-sibling::b/text()="Anschrift"]'
        ).getall()
        name = title[0]
        specialty = title[1]
        focus = title[2:]

        tel = response.xpath(
            '//div[@id="form:j_id_4a_content"]').re_first(self.tel)
        fax = response.xpath(
            '//div[@id="form:j_id_4a_content"]').re_first(self.fax)

        email = response.xpath(
            '//div[@id="form:j_id_4a_content"]//text()'
            '[contains(., "Email:")]/following-sibling::a/@href'
        ).get()

        website = response.xpath(
            '//div[@id="form:j_id_4a_content"]//text()'
            '[contains(., "Internet:")]/following-sibling::a/@href'
        ).get()

        pers_conhrs = response.xpath(
            '//div[@id="form:j_id_4a_content"]'
            '/b[text()="Persönliche Sprechstunden"]/following-sibling::div'
            '[contains(@class, "oeffnungszeiten") and position() = 1]'
            '/div/ul/li/text()'
        ).getall()

        inf_conhrs = response.xpath(
            '//div[@id="form:j_id_4a_content"]'
            '/b[text()="Infekt Sprechstunde"]/following-sibling::div'
            '[contains(@class, "oeffnungszeiten") and position() = 1]'
            '/div/ul/li/text()'
        ).getall()

        tel_conhrs = response.xpath(
            '//div[@id="form:j_id_4a_content"]'
            '/b[text()="Telefonische Erreichbarkeit"]/following-sibling::div'
            '[contains(@class, "oeffnungszeiten") and position() = 1]'
            '/div/ul/li/text()'
        ).getall()

        item = {
            'Name': name, 'Telephone': tel, 'Fax': fax, 'Email': email,
            'Website': website, 'Street': street, 'City': city, 'ZIP': ZIP,
            'Specialty': specialty, 'Focus': focus,
            'Practice Form': pracform, 'Practice': practice,
            'Personal Consultation Hours': ' | '.join(pers_conhrs),
            'Infection Consultation Hours': ' | '.join(inf_conhrs),
            'Telephone Availibility': ' | '.join(tel_conhrs)
        }

        # Retrieve subsequent entry.
        next_i = ent_i + 1
        self.logger.debug(
            f'Proceeding to crawl entry {next_i}'
            f'in session {response.meta["cookiejar"]}'
        )
        jsf_viewstate = response.xpath(
            '//update[@id="j_id__v_0:javax.faces.ViewState:1"]/text()'
        ).get()
        yield FormRequest(
            url='https://arztsuche.kvsh.de/suche.do',
            headers={'Faces-Request': 'partial/ajax'},
            formdata={
                'javax.faces.partial.ajax': 'true',
                'javax.faces.source': f'form:arztErgebnis:{next_i}:j_id_45',
                'javax.faces.partial.execute': '@all',
                'javax.faces.partial.render':
                    'form:suchergebnis+form:suchEingabe',
                f'form:arztErgebnis:{next_i}:j_id_45':
                    f'form:arztErgebnis:{next_i}:j_id_45',
                'form:ausgewaehlterArzt_input': '',
                'form:ausgewaehlterArzt_hinput': '',
                'form:ausgewaehlterOrt_input': response.meta['cookiejar'],
                'form:ausgewaehlterOrt_hinput': response.meta['cookiejar'],
                'form:ausgewaehltesFachgebiet_input': '-+egal+-',
                'form_SUBMIT': '1',
                'javax.faces.ViewState': jsf_viewstate
            },
            meta={
                'proxy': 'localhost:24001',
                'cookiejar': response.meta['cookiejar']
            },
            callback=self.parse_profile_data,
            cb_kwargs={'ent_i': next_i}
        )
        yield item
