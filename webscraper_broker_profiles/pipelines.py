# Define pipelines here. Don't forget to add your pipelines to the
# ITEM_PIPELINES setting individually to you spider's custom_settings.

# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from re import compile as regex
from pkg_resources import resource_filename
import csv

class NameCleaner:
    """
    Fixes capitalisation errors and srtips off extraneous names of
    partners/team members and any post-nominal qualifications.
    """

    def process_item(self, item, spider):
        adaptor = ItemAdapter(item)
        if adaptor.get('name'):
            adaptor['name'] = adaptor['name'].title()
            adaptor['name'] = adaptor['name'].split('And')[0]
            adaptor['name'] = adaptor['name'].split(',')[0]
        return item

class CityCleaner:
    """
    Currently, only fixes capitalisation errors.
    """

    def process_item(self, item, spider):
        adaptor = ItemAdapter(item)
        if adaptor.get('city'):
            adaptor['city'] = adaptor['city'].title()
        return item

class StateNameEncoder:
    """
    If names of state are spelled out, enabling this will convert them to their
    standard 2-letter code. Don't enable otherwise!
    """

    def open_spider(self, spider):
        with open(
            resource_filename(
                'brokerage_info_crawler.static_data',
                'us_state_codes.csv'
            ),
            newline=''
        ) as codesf:
            codes = csv.reader(codesf)
            self.codes = dict(entry[0:2] for entry in codes)

    def process_item(self, item, spider):
        adaptor = ItemAdapter(item)
        if adaptor.get('state'):
            adaptor['state'] = self.codes.get(
                adaptor['state'].title(), adaptor['state']
            )
        return item

class NumberCleaner:
    """
    Cleans all noise which is characters that aren't digits
    from phone numbers.
    """

    numbers = regex(r'\d+')

    def process_item(self, item, spider):
        adaptor = ItemAdapter(item)
        if adaptor.get('phone'):
            adaptor['phone'] = ''.join(self.numbers.findall(adaptor['phone']))
        if adaptor.get('phone_alt'):
            adaptor['phone_alt'] = ''.join(
                self.numbers.findall(adaptor['phone_alt'])
            )
        if adaptor.get('work_tel'):
            adaptor['work_tel'] = ''.join(
                self.numbers.findall(adaptor['work_tel'])
            )

        return item
