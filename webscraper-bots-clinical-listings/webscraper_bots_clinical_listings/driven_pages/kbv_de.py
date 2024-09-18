from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from webscraper_bots_clinical_listings.driven_pages import WebPage
from webscraper_bots_clinical_listings import settings
from time import sleep


class SearchPage(WebPage):
    """Driven page to control the page for doctor search at arztsuche.kbv.de.

    Important: This excepts all click interceptions caused by the human
    verification popups on the page.
    """

    URL = 'https://arztsuche.kbv.de/pages/arztsuche.xhtml'

    def __init__(self, driver=None, *args, **kwargs):
        """
        If driver is not specified, constructs one and navigates
        to the search page.
        """

        super().__init__(*args, **kwargs)
        self._driver.maximize_window()
        if driver:
            return

        self._driver.get(self.URL)

    def refresh(self, *args, **kwargs):
        super().refresh(*args, **kwargs)
        try:
            self.wait.until(EC.alert_is_present())
            self.alert.accept()
        except TimeoutException:
            pass
        sleep(settings.DEFAULT_WAIT_TIMEOUT)

    def consent2cookies(self):
        """Accept cookie policy notice if it poped up."""

        try:
            popup = self.select(css='div.dsgvo-cookie.start')
        except NoSuchElementException:
            popup = None
        if popup:
            popup.find_element_by_class_name('accept-all').click()

    def search(self, zip_):
        """Fill ZIP and submit form."""

        dropdown = self.select(css='#select2-asLocation-container')
        dropdown.click()
        field = self.select(css='.select2-search__field[role="textbox"]')
        for c in zip_ + Keys.ENTER:
            sleep(3)
            field.send_keys(c)
        submit = self.select(css='#searchForm\\:startSearch')
        submit.click()

    def open_result(self, entry):
        """Open entry for doctor.

        Parameters
        entry - Entry's data-arzt-id attribute or WebElement.
        """

        if type(entry) is str:
            entry = self.select(css=f'div[data-arzt-ids="{entry}"]')
        entry.click()
        self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#arztDetailsDialog button.close')))
        return self.select(css='#arztDetailsDialog div.container-fluid')

    def close_dialog(self, dialog):
        """Close details dialog.

        Uses provided element reference to close an already present dialog.

        Parameters
        dialog - WebElement for the dialog.
        """

        dialog.find_element(By.CSS_SELECTOR, 'button.close').click()

    def discard(self):
        self._driver.close()
