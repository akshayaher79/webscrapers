#!python

from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from webscraper_bots_clinical_listings.driven_pages.kbv_de import SearchPage
from webscraper_bots_clinical_listings import settings
from webscraper_bots_clinical_listings.utils import _try
from pkg_resources import resource_stream
import psycopg2


def main():
    with resource_stream('webscraper_bots_clinical_listings.static_data', 'ZIPs/NO.txt') as zips, \
         SearchPage() as searchpage:

        def search(zip_):
            _try(
                to      = lambda: searchpage.search(zip_),
                on_exc  = lambda: (searchpage.refresh(clear_cookies=True),
                                   searchpage.consent2cookies()),
                exc     = (ElementNotInteractableException,
                           ElementClickInterceptedException,
                           NoSuchElementException)
            )

        dbcnx = psycopg2.connect(**settings.DB_CREDENTIALS)
        cursor = dbcnx.cursor()
        for zip_ in zips:
            zip_ = str(zip_, encoding='utf-8').rstrip()

            search(zip_)
            entries = _try(
                to      = lambda: searchpage.select('#searchResultList'
                          ).find_elements_by_css_selector('div[data-arzt-ids]'),
                on_exc  = lambda: search(zip_),
                exc     = NoSuchElementException

            )

            ids = [e.get_attribute('data-arzt-ids') for e in entries]
            for id in ids:
                dialog = _try(
                    to      = lambda: searchpage.open_result(id),
                    on_exc  = lambda: search(zip_),
                    exc     = (TimeoutException, NoSuchElementException)
                )

                data = dialog.get_property('innerHTML')

                with dbcnx:
                    cursor.execute(
                        "INSERT INTO raw_html.whole_entries (source, id_source, html) " \
                            "VALUES (%(source)s, %(id_source)s, %(html)s) " \
                            "ON CONFLICT (source, id_source) DO UPDATE " \
                                "SET html = %(html)s;",
                        {'source': 'KVB', 'id_source': id, 'html': data}
                    )

                try:
                    searchpage.close_dialog(dialog)
                except (ElementClickInterceptedException,
                        ElementNotInteractableException,
                        StaleElementReferenceException):
                    pass

        cursor.close()
        dbcnx.close()

if __name__ == "__main__":
    main()
