from scrapy import Spider
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from shutil import which


def normalise_space(s):
    return ' '.join(filter(None, map(str.strip, s.split())))


class KvbbDe(Spider):
    name = 'kvbb.de'
    allowed_domains = ['arztsuche.kvbb.de']

    custom_settings = {
        'SELENIUM_DRIVER_NAME': 'firefox',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': which('geckodriver'),
        'SELENIUM_DRIVER_ARGUMENTS': ['-headless'],

        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 800
        }
    }

    def start_requests(self):
        return [
            SeleniumRequest( # Doctor directory
                url='https://arztsuche.kvbb.de'
                    '/ases-kvbb/ases.jsf?t=arzt',
                callback=self.parse_doc_dir
            ),
            SeleniumRequest( # Psychotherapist directory
                url='https://arztsuche.kvbb.de'
                    '/ases-kvbb/ases.jsf?t=psychotherapeut',
                callback=self.parse_psych_dir
            )
        ]

    # These two parse increasingly smaller fragments of the
    # documents through multiple steps and construct fields
    # from each step into items. The earlier steps parse
    # broad elements out and leave deeper parsing to further
    # steps. These are separate to accomodate a few minor
    # variations in entry formats between the two directories.
    def parse_doc_dir(self, response):
        for entry in self.parse_results_section(response):
            entry, subentries = self.parse_entry(entry)
            for subentry in subentries:
                # Extra fields
                open_days = subentry.xpath(
                    './/div[@class="ases-leistungsort-oeffnungszeiten-table"]'
                    '/div[contains(@class, "ases-oeff-tag")]'
                )
                hours = []
                for day in open_days:
                    day_name = day.xpath(
                        'span[@class="ases-oeff-tag-name"]/text()'
                    ).get()
                    timings  = day.xpath(
                        'div[@class="ases-oeff-zeiten-list"]'
                        '/div[@class="ases-oeff-block"]'
                    )
                    timings = ', '.join(
                        normalise_space(t.xpath('string()').get())
                        for t in timings
                    )
                    hours.append(f'{day_name} {timings}')
                hours = ' | '.join(hours)

                subentry = self.parse_subentry(subentry)
                yield {
                    'Arzttyp': 'Arzt',
                    **entry,
                    **subentry,
                    'Sprechstunde': hours
                }

    def parse_psych_dir(self, response):
        for entry in self.parse_results_section(response):
            entry, subentries = self.parse_entry(entry)
            for subentry in subentries:
                # Extra fields
                method = subentry.xpath(
                    '//div[@class="ases-arzt-zusatzinfos"]/div/ul/li'
                    '/b[contains(text(), "Therapieverfahren:")]'
                    '/following-sibling::text()[normalize-space()]'
                ).get()
                method = normalise_space(method) if method else ''

                open_days = subentry.xpath(
                    './/div[@class="ases-lo-te-header"]'
                    '/following-sibling::div[1]/div'
                    '/table/tbody/tr'
                )
                hours = []
                for day in open_days:
                    day_name = day.xpath(
                        'td[@class="ases-te-data-table-day"]/div/text()'
                    ).get()
                    day_name = day_name if day_name else ''
                    timings  = day.xpath(
                        'td[@class="ases-te-data-table-te-time"]'
                        '/label/text()'
                    ).get()
                    timings = timings if timings else ''
                    hours.append(f'{day_name} {timings}')
                hours = ' | '.join(hours)

                subentry = self.parse_subentry(subentry)
                yield {
                    'Arzttyp': 'Psychotherapeut',
                    **entry,
                    **subentry,
                    'Sprechstunde': hours,
                    'Therapieverfahren': method
                }

    # These helpers implement each parsing step.
    def parse_results_section(self, response):
        driver = response.request.meta['driver']
        driver.maximize_window()
        driver.implicitly_wait(10)

        wait = WebDriverWait(driver, 10)

        # Submit empty form
        driver.find_element_by_id(
            'asesInputForm:searchCriteria'
        ).send_keys(Keys.ENTER)

        # Page size control
        Select(
            wait.until(
                EC.presence_of_element_located(
                    (By.ID, 'arztlisteDataList_rppDD')
        ))).select_by_value('50')
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.ases-arzt-eintrag:nth-child(50)')
        ))

        npages = int(
            driver.find_element_by_class_name('ui-paginator-current'
            ).get_property('innerText').strip().split()[-1]
        )
        for pnum in range(1, npages+1):
            for entry_i, entry in enumerate(
                driver.find_elements_by_class_name(
                    'ases-arzt-eintrag'
            )):
                ntabs = len(
                    entry.find_elements_by_css_selector('.ui-tabs-nav li > a')
                )
                for tab_i in range(1, ntabs+1):
                    entry.find_element_by_css_selector(
                        f'.ui-tabs-nav > li:nth-child({tab_i}) > a'
                    ).click()
                    wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR,
                             f'.ases-arzt-eintrag:nth-child({entry_i+1}) '
                             f'div[role=tabpanel]:nth-child({tab_i}) > div'
                            )
                    ))
                yield Selector(text=entry.get_property('innerHTML'))
            self.logger.debug(
                f'Crawled result page number {pnum} of {npages} '
                f'at {response.request.url}.'
            )

            # Next page button
            driver.find_element_by_css_selector(
                '#arztlisteDataList_paginator_bottom '
                '> span.ui-paginator-next'
            ).click()
            wait.until(
                EC.text_to_be_present_in_element(
                    (By.CLASS_NAME, 'ui-paginator-current'),
                    f'Seite {pnum} von {npages}'
            ))

    def parse_entry(self, entry):
        name = entry.xpath(
            '//div[@class="ases-arzt-name-fachgebiet-text"]/a/span/text()'
        ).get()

        expertise = entry.xpath(
            '//div[@class="ases-arzt-name-fachgebiet-text"]'
            '/a/text()[normalize-space()]'
        ).getall()
        expertise = '; '.join(e.strip() for e in expertise)

        lang = entry.xpath(
            '//div[@class="ases-arzt-zusatzinfos"]/div/ul/li'
            '/b[contains(text(), "Fremdsprachen:")]'
            '/following-sibling::text()[normalize-space()]'
        ).get()
        lang = normalise_space(lang) if lang else ''

        add_desig = entry.xpath(
            '//div[@class="ases-arzt-zusatzinfos"]/div/ul/li'
            '/b[contains(text(), "Zusatzbezeichnungen:")]'
            '/following-sibling::text()[normalize-space()]'
        ).get()
        add_desig = normalise_space(add_desig) if add_desig else ''

        add_act = entry.xpath(
            '//div[@class="ases-arzt-zusatzinfos"]/div/ul/li'
            '/b[contains(text(), "Zusatzangebote:")]'
            '/following-sibling::text()[normalize-space()]'
        ).get()
        add_act = normalise_space(add_act) if add_act else ''

        subentries = entry.xpath(
            '//div[@class="ui-tabs-panels"]/div[@role="tabpanel"]'
        )

        return (
            {
                'Name': name,
                'Fachgebiet': expertise,
                'Fremdsprachen': lang,
                'Zusatzbezeichnungen': add_desig,
                'Zusatzangebote': add_act
            },
            subentries
        )

    def parse_subentry(self, subentry):
        street = subentry.xpath(
            '//ul[@role="tablist"]/li[@role="tab" and '
                'position() = $subentry_index]'
            '/a/div/input[@class="ases-selector-hidden-arzt"]'
            '/@data-leistungsort-strasse'
        ).get()
        postalcode = subentry.xpath(
            '//ul[@role="tablist"]/li[@role="tab" and '
                'position() = $subentry_index]'
            '/a/div/input[@class="ases-selector-hidden-arzt"]'
            '/@data-leistungsort-plz'
        ).get()
        city = subentry.xpath(
            '//ul[@role="tablist"]/li[@role="tab" and '
                'position() = $subentry_index]'
            '/a/div/input[@class="ases-selector-hidden-arzt"]'
            '/@data-leistungsort-ort'
        ).get()

        phone = subentry.xpath(
            './/i[contains(@class, "fa-phone")]'
            '/following-sibling::text()[normalize-space()]'
        ).getall()
        phone = '; '.join(p.strip() for p in phone)

        website = subentry.xpath(
            './/i[contains(@class, "fa-globe")]'
            '/following-sibling::a/@href'
        ).get()

        prac_form = subentry.xpath(
            './/div[@class="ases-leistungsort-kontaktdaten-header"]'
            '/following-sibling::ul[1]/li[1]/text()'
        ).get()
        prac_form = prac_form.strip() if prac_form else ''

        assoc = subentry.xpath(
            './/div[@class="ases-leistungsort-kontaktdaten-header"]'
            '/following-sibling::ul[1]/li[2]/text()'
        ).get()
        assoc = assoc.strip() if assoc else ''

        focus = subentry.xpath(
            './/div[@class="ases-leistungsort-taetigkeit"]/ul/li'
            '/b[contains(text(),"Schwerpunkte:")]'
            '/following-sibling::text()[normalize-space()]'
        ).get()
        focus = normalise_space(focus) if focus else ''

        add_act = subentry.xpath(
            './/div[@class="ases-leistungsort-taetigkeit"]/ul/li'
            '/b[contains(text(),"Zusatzangebote:")]'
            '/following-sibling::text()[normalize-space()]'
        ).get()
        add_act = normalise_space(add_act) if add_act else ''

        return {
            'Strasse': street,
            'PLZ': postalcode,
            'Ort': city,
            'Telefon': phone,
            'Website': website,
            'Praxisform': prac_form,
            'BAG mit': assoc,
            'Schwerpunkte': focus,
            'Mehr Zusatzangebote': add_act
        }
