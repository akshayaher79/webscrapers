from setuptools import setup, find_packages
import os

BOTS = [f'webscraper_bots_clinical_listings/bots/{bot}' for bot in os.listdir('webscraper_bots_clinical_listings/bots')]
BOTS.remove('webscraper_bots_clinical_listings/bots/__init__.py')

setup(
    name         = 'webscraper-bots-clinical-listings',
    version      = '1.0',
    description  = 'Collection of Selenium-based bots to scrape data from '
                   'German clinical listing websites.',
    install_requires = ['selenium', 'psycopg2-binary', 'lxml'],
    scripts      = BOTS,
    packages     = find_packages(),
    include_package_data = True,
    package_data = {
        'webscraper_bots_clinical_listings.static_data': ['*', '*/*']
    }
)
