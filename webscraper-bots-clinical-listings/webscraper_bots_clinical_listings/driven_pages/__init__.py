"""Modules with "driven pages" for each website.

Driven pages are abstractions of webpages associated with particular sets of
automated interactions the bots may perform on them. These accomplish tasks
such as filling/extracting a field. Only these communicate with the proxy
driver.
"""

# Each website will have a module with subclasses of the WebPage class defined
# below that collect desired actions possible on a page.

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.alert import Alert
from webscraper_bots_clinical_listings import settings
from os import getenv
from sys import platform


class WebPage:
    """Informal interface for driven pages."""

    def __init__(self, driver=None):
        """
        Default driver initialises for headless Firefox with proxy settings
        and implicit wait.
        """

        if not driver:
            dc = DesiredCapabilities.FIREFOX.copy()
            settings.PROXY.add_to_capabilities(dc)

            options = Options()
            if not getenv('DISPLAY') or platform == 'win32':
                options.add_argument('-headless')

            driver = Firefox(desired_capabilities=dc, options=options)
            driver.implicitly_wait(settings.DEFAULT_IMPLICIT_WAIT)

        self._driver = driver
        self.wait = WebDriverWait(driver, settings.DEFAULT_IMPLICIT_WAIT)
        self.alert = Alert(driver)

    # Context manager support.
    # Allows usage of the with statement as in
    # with page as SomePage():
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.discard()
        return False

    def refresh(self, clear_cookies=False):
        if clear_cookies:
            self._driver.delete_all_cookies()
        self._driver.refresh()

    # These two are shortcuts to make driven page implementations more readable.
    def select(self, css=None, xpath=None):
        """Select one element using CSS selector or XPath expression."""

        if css:
            return self._driver.find_element_by_css_selector(css)
        elif xpath:
            return self._driver.find_element_by_xpath(xpath)

    def select_all(self, css=None, xpath=None):
        """Select elements using CSS selector or XPath expression."""

        if css:
            return self._driver.find_elements_by_css_selector(css)
        elif xpath:
            return self._driver.find_elements_by_xpath(xpath)

    def discard(self):
        """Close this page or relinquish it without affecting shared state.

        For instance, this must navigate or switch back to the previous page or
        tab instead of closing the window in order to preserve other open pages.
        """

        pass
