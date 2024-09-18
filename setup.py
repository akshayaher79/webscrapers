# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'webscraper-broker-profiles',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = webscraper_broker_profiles.settings']},
    include_package_data = True,
    package_data = {
    'webscraper_broker_profiles.static_data': ['*']
    }
)
