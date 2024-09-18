from scrapy import Spider


class KvhbDe(Spider):

    name = 'kvhb.de'
    allowed_domains = ['kvhb.de']

    # There 4 different search portals in the website's doctor search section.
    start_urls = [
        # Fachärzte
        'https://www.kvhb.de/dsearch/fach%C3%A4rzte'
        '?option_doctors_name=&option_fachrichtung=0'
        '&option_zusatzbezeichnung=0'
        '&radio1=bremen&barrierefreiheit=0&option_fremdsprachen=0&op=SUCHEN'
        '&form_build_id=form-0of86eBJ4WVYomlF19YYU83JNZAnd1lY1DPsk7e8Ucc'
        '&form_id=doctor_search_form',

        # Hausärzte
        'https://www.kvhb.de/dsearch/haus%C3%A4rzte'
        '?option_doctors_name=&radio1=bremen&barrierefreiheit=0'
        '&option_fremdsprachen=0&op=SUCHEN'
        '&form_build_id=form-MiPeHxd4uV_beNdZCZWP3S9JN0TKAya3LhNB_lYfFEo'
        '&form_id=doctor_search_form',

        # Kinder- und Jugendärzte
        'https://www.kvhb.de/dsearch/kinder%C3%A4rzte'
        '?option_doctors_name=&radio1=bremen&barrierefreiheit=0'
        '&option_fremdsprachen=0&op=SUCHEN'
        '&form_build_id=form-MIuCUvP7K9VWR7W94SvpZU53j226Z2WjEIvNwkc6OdI'
        '&form_id=doctor_search_form',

        # Psychotherapeuten
        'https://www.kvhb.de/dsearch/psychotherapeuten'
        '?option_doctors_name='
        '&option_psychotherapeuten%5Bpsychologische_psychotherapeuten%5D'
        '=psychologische_psychotherapeuten'
        '&option_psychotherapeuten%5B%C3%A4rztliche_psychotherapeuten%5D'
        '=%C3%A4rztliche_psychotherapeuten'
        '&option_therapieform=tfalle'
        '&option_group=einzelGroupAlle'
        '&option_alter=f%C3%BCr_erwachsene&radio1=bremen&barrierefreiheit=0'
        '&option_fremdsprachen=0&op=SUCHEN'
        '&form_build_id=form-3eJcQWZ5hUoy0tK8uxoHYPonauNbZy7d35d19rFjATg'
        '&form_id=doctor_search_form'
    ]

    def parse(self, response):
        yield from response.follow_all(
            css='.name a',
            callback=self.parse_profile
        )

        next = response.css('.pager-next a')
        if next:
            yield response.follow(
                url=next[0],
                callback=self.parse
            )

    def parse_profile(self, response):
        name = response.css('#center  h1::text').get()
        specs = response.css('.speciality::text').getall()
        add_acts = response.css('.einzelgruppe::text').get()

        office = response.css('#office-info .row')
        langs = None
        pracform = None
        assocs = None
        if office:
            langs = office[0].css('::text').get()
        if office[1:]:
            pracform = office[1].css('::text').get()
            assocs = office[1].css('span > a::text').getall()

        hours = ', '.join(
            day.css('.day-title::text').get() + ' '
            + ' | '.join(day.css('.time::text').getall())
            for day in response.css('#sprechstunde .day')
        )
        tel_hrs = response.css('#vereinbarung::text').get()

        address = response.css('#address .text::text').getall()
        street = address[0]
        ZIP, city = address[1].split(' ', maxsplit=1)

        phone = response.xpath(
            '//div[contains(@id, "telefon")]'
            '/label[contains(text(), "Telefon:")]'
            '/following-sibling::span/text()'
        ).get()
        fax = response.xpath(
            '//div[contains(@id, "telefon")]'
            '/label[contains(text(), "Fax:")]'
            '/following-sibling::span/text()'
        ).get()

        website = response.css('#website a::attr(href)').get()

        return {
            'Name': name,
            'Activities of Focus': specs,
            'Additional Activites': add_acts,
            'Languages': langs,
            'Hours': hours,
            'Telephone Hours': tel_hrs,
            'Street': street,
            'City': city,
            'ZIP': ZIP,
            'Phone': phone,
            'Fax': fax,
            'Website': website,
            'Practice Form': pracform,
            'Associates': assocs
        }
