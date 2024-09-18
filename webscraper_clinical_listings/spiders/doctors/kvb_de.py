from scrapy import Spider
from scrapy.http import FormRequest
from pkg_resources import resource_filename


class kvb_de(Spider):

    name = 'kvb.de'
    allowed_domains = ['dienste.kvb.de']

    start_urls = ['https://dienste.kvb.de/arztsuche/app/erweiterteSuche.htm']
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1
    }

    # Fills the form at the start page and submits a query for every ZIP.
    def parse(self, response):
        with open(
            resource_filename(
                'doc_info_crawler.static_data', 'ZIPs/BY.txt'
            )
        ) as zipsf:
            for zip_ in zipsf:
                yield FormRequest.from_response(
                    response, callback=self.parse_result_page,
                    formdata={
                        'adresse': zip_.rstrip()
                    }
                )

    def parse_result_page(self, response):
        yield from response.follow_all(
            css='.titel_name_zelle > a',
            callback=self.parse_profile
        )
        next = response.css(
            '.suchergebnisse_navigationsbalken_zelle_rechts form'
        )
        if next:
            # Form for next page query
            yield FormRequest.from_response(
                response, callback=self.parse_result_page,
                formcss='.suchergebnisse_navigationsbalken_zelle_rechts form'
            )

    def parse_profile(self, response):
        name = response.css('.titel_name_zelle > a::text').get()
        doctype = response.css('.arztart_zelle::text').get()
        expertise = response.css('.fachgebiet_zelle::text').get()
        add_qual = response.css('zusatzinfo_titel::text').getall()
        pracform = response.css('.adresse_zelle.leere_zeile span::text').get()
        assocs = response.css('.arzt_name font font::text ').getall()
        approval = response.css(
            '.suchergebnisse_zusatzinfo_zweite_spalte .zusatzinfo_text::text'
        ).getall()

        address = response.css('.adresse_tabelle tr::text').getall()

        phone = response.xpath(
            '//table[contains(@class, "tel_tabelle")]'
            '//td[contains(text(), "Tel.:")]/following-sibling::td::text'
        ).get()

        fax = response.xpath(
            '//table[contains(@class, "tel_tabelle")]'
            '//td[contains(text(), "Fax.:")]/following-sibling::td::text'
        ).get()

        website = response.xpath(
                '//table[contains(@class, "tel_tabelle")]'
                '//td[contains(text(), "Web:")]/following-sibling::td::text'
        ).get()

        email = response.css(
                '//table[contains(@class, "tel_tabelle")]'
                '//td[contains(text(), "E-Mail:")]/following-sibling::td/a::text'
        ).get()
        hours = response.css('.sprechzeiten_tabelle tr:text').getall()

        return {
            'Name': name,
            'Doctype': doctype,
            'Tätigkeitsbereiche (Fachgruppe)': expertise,
            'Zusatzbezeichnungen': '|'.join(add_qual),
            'Praxisform': pracform,
            'Hours': '|'.join(hours),
            'Genehmigungen': '|'.join(approval),
            'Berufsausübungsgemeinschaft mit': '|'.join(assocs),
            'Address': '|'.join(address),
            'Phone': phone,
            'Fax': fax,
            'Email': email,
            'Website': website
        }
