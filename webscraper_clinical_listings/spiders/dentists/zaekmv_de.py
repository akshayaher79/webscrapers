from scrapy import (Spider, Request)
import json
from pkg_resources import resource_string


class ZaekmvDeSpider(Spider):
    name = 'zaekmv.de'
    allowed_domains = ['zaekmv.de']
    start_urls = [
        'https://www.zaekmv.de'
        '/uploads/bw_zaekmv_import/data/searchTags.json'
    ]

    category_codes = json.loads(
        resource_string(
            'doc_info_crawler.static_data',
            'zaekmv.de_categories_encoding.json'
        )
    )

    def parse(self, response):
        for item in response.json():
            yield Request(
                url='https://www.zaekmv.de'
                    '/uploads/bw_zaekmv_import/data'
                    f'/doctors/doctor_{item["uid"]}.json',
                callback=self.parse_profile
            )

    def decode_category(self, code):
        decoding = {
            'activities_focus': '',
            'activities_office': '',
            'activities_study': ''
        }
        if not code:
            return decoding

        groups = {
            '35': 'activities_focus',
            '55': 'activities_office',
            '24': 'activities_study'
        }
        for grp, grpitems in code.items():
            decoding[groups[grp]] = '; '.join(
                self.category_codes[grp][gi] for gi in grpitems
            )
        return decoding

    def parse_profile(self, response):
        item = response.json()
        new_item = self.decode_category(item['categories'])

        title = 'Herr' if int(item['gender']) == 1 else 'Frau'
        new_item['name'] = ' '.join(
            filter(
                None,
                [
                 title, item['address_title'],
                 item['address_firstname'], item['address_lastname']
                ]
            )
        )
        new_item['medical_specialist'] = item['job_description']

        new_item['BAG_mit'] = ' '.join(
            filter(
                None,
                [item['address_name2'], item['address_name3']]
            )
        )

        new_item['street'] = item['address_street']
        new_item['postal_code'] = item['address_zip']
        new_item['city'] = item['address_city']
        new_item['alt_postal_code_city'] = item['address_alternative_zip_city']
        new_item['alt_street'] = item['address_alternative_street']

        new_item['website'] = item['internet']
        new_item['email'] = item['email']
        new_item['telephone'] = item['phone']
        new_item['telephone_emergency'] = item['phone_emergency']
        new_item['telefax'] = item['fax']

        new_item['emergency_opening'] = item['emergency_opening']
        new_item['emergency_opening2'] = item['emergency_opening2']

        return new_item
