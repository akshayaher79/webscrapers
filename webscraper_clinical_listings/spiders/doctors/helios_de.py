from scrapy import Spider
from pkg_resources import resource_filename


class HeliosGesundheit(Spider):

    name = 'helios_gesundheit.de'
    allowed_domains = ['helios-gesundheit.de']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open(
            resource_filename(
                'doc_info_crawler.static_data', 'start_urls/helios.de.txt'
            )
        ) as start_urlsf:
            self.start_urls = start_urlsf.readlines()

    def parse(self, response):
        yield from response.follow_all(
            css='div.almanac__item a.link-list__link',
            callback=self.parse_department,
            cb_kwargs={
                'history': [response.request.url]
            }
        )

    def parse_department(self, response, history):
        team_path = response.xpath(
            '//a[contains(text(), "Unser Team")]/@href | '
            '//div[contains(@class, "department-contact-team__cta")]/a/@href'
        ).get()

        if team_path is not None:
            # Team page link
            yield response.follow(
                url=response.urljoin(team_path),
                callback=self.parse_team,
                cb_kwargs={
                    'history': history + [response.request.url]
                }
            )
        else:
            # Any profile links present on the page
            yield from response.follow_all(
                css='.person-teaser__link',
                callback=self.parse_profile,
                cb_kwargs={
                    'history': history + [response.request.url]
                }
            )

    def parse_team(self, response, history):
        yield from response.follow_all(
            css='.person-teaser__link',
            callback=self.parse_profile,
            cb_kwargs={
                'history': history + [response.request.url]
            }
        )

    def parse_profile(self, response, history):
        title = response.css('.person-header__label::text').get()
        first_name = response.css(
            '.person-header__name span:nth-child(1)::text'
        ).get()
        last_name = response.css(
            '.person-header__name span:nth-child(2)::text'
        ).get()
        position = response.css(
            '.person-header__position::text'
        ).get()

        qual_spec = response.css(
            '.block-text p::text, .block-text ul li::text'
        ).getall()

        qualifications = []
        specilaisations = []
        for item in qual_spec:
            if "Facharzt" in item or "Fachärztin" in item:
                qualifications.append(item.strip())
            else:
                specilaisations.append(item.strip())

        email = response.css('[itemprop=email]::attr(href)').get()
        phone = response.css('[itemprop=telephone]::text').get()
        fax = response.css('[itemprop=faxNumber]::text').get()

        clinic_name = response.css('.clinic-branding__text::text').get()
        if clinic_name:
            clinic_name = clinic_name.strip()
        departments = response.xpath(
            '//h3[contains(text(), "Fachbereiche")]'
            '/ancestor::section//li/a/text()'
        ).getall()

        return {
            'Crawl Steps': ' '.join(history + [response.request.url]),
            'Hospital Name': clinic_name,
            'Departments': '; '.join(departments),
            'Title': title,
            'First Name': first_name,
            'Last Name': last_name,
            'Position': position,
            'Specialisation': '; '.join(specilaisations),
            'Qualification': '; '.join(qualifications),
            'Email': email,
            'Telephone': phone,
            'Fax': fax
        }
