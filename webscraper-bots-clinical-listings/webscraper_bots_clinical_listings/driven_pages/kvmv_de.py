from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from webscraper_bots_clinical_listings.driven_pages import WebPage
from time import sleep
from urllib.parse import urljoin

class SearchPage(WebPage):

    URL = "https://www.kvmv.de/ases-kvmv/ases.jsf"

    def __init__(self, search='arzt', driver=None, *args, **kwargs):
        """
        If driver is not specified, constructs one and navigates
        to the specified search page.
        """

        super().__init__(*args, **kwargs)
        self._driver.maximize_window()
        if driver:
            return

        if search not in ['arzt', 'psychotherapeut']:
            raise ValueError('Argument for search parameter not recognised.')
        else:
            self._driver.get(urljoin(self.URL, f'?t={search}'))

    def iterate_results_categories(self, criteria):
        """Iteratively filter resultsets of categories by given criteria."""

        box = {
            'xpath': '//div[@class="ases-aggregation-box-attribut" '
                    f'and h2/text()="{criteria}"]'
        }
        expander = {
            'xpath': box['xpath'] +\
                     '//div[contains(@class,'
                     '"ases-aggregation-filter-element-expand")]'
        }
        cats = {
            'xpath': box['xpath'] +\
                     '//div[@class="ases-aggregation-filter-element ui-widget-content"]'
        }
        canceller = {
            'xpath': box['xpath'] +\
                     '//div[contains(@class,'
                     '"ases-aggregation-filter-remove") '
                     'and contains(string(), "Filter entfernen")]'
        }

        if not self.select(**box):
            return

        try:
            self.select(**canceller).click()
            sleep(5)
        except NoSuchElementException:
            pass

        try:
            self.select(**expander).click()
            sleep(5)
        except NoSuchElementException:
            pass
        cats_ = self.select_all(**cats)

        for i in range(len(cats_)):
            sleep(5)
            name = cats_[i].find_element_by_class_name(
                'ases-aggregation-filter-key'
            ).get_property('innerText')
            count = int(cats_[i].find_element_by_class_name(
                'ases-aggregation-filter-value'
            ).get_property('innerText').strip('()'))

            cats_[i].click()
            sleep(5)
            yield (i, name, count)

            self.select(**canceller).click()
            try:
                self.select(**expander).click()
                sleep(5)
            except NoSuchElementException:
                pass

            cats_ = self.select_all(**cats)

    def maximise_page_size(self):
        """Set pagination size to max value."""

        try:
            psize_ctrl = self.select(
                css='#arztlisteDataList_rppDD'
            )
        except NoSuchElementException:
            return

        max_opt = self.select(
            css='#arztlisteDataList_rppDD option:last-child'
        ).get_attribute('value')
        Select(psize_ctrl).select_by_value(max_opt)

    def iterate_results(self):
        """Iterate result panels, fully expanding each one."""

        nentries = len(self.select_all('.ases-arzt-eintrag'))
        for e in range(1, nentries + 1):
            ntabs = len(
                self.select_all(
                    f'.ases-arzt-eintrag:nth-child({e}) .ui-tabs-nav li > a'
                )
            )
            for t in range(1, ntabs + 1):
                sleep(5)
                tab = self.select(
                    f'.ases-arzt-eintrag:nth-child({e}) ' \
                    f'.ui-tabs-nav > li:nth-child({t}) > a'
                )
                try:
                    tab.click()
                except (ElementNotInteractableException,
                        ElementClickInterceptedException):

                	self.select(
                           f'.ases-arzt-eintrag:nth-child({e}) '
                            'a.ui-tabs-navscroller-btn-right'
                	).click()
                	sleep(1)
                	tab.click()

            sleep(3)
            yield self.select(f'.ases-arzt-eintrag:nth-child({e})')

    def discard(self):
        self._driver.quit()

