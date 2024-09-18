from scrapy import Spider
from scrapy.http import FormRequest
from pkg_resources import resource_filename
from re import compile as regex


class KzvthDe(Spider):

    name = 'kzvth.de'
    allowed_domains = ['kzvth.de']

    def start_requests(self):
        with open(
            resource_filename('doc_info_crawler.static_data', 'ZIPs/TH.txt')
        ) as zips:
            for zip_ in zips:
                query = {
                    'zipCode': zip_.strip(),
                    'startIndex': '1',
                    'pageSize': '10'
                }
                yield FormRequest(
                    url='https://info.kzvth.de/ZaSuche/GetZaPaged',
                    method='GET',
                    formdata=query,
                    cb_kwargs=query
                )

    assoc_pfix = regex(
        r'\b(Überörtl\. )?Berufsausübungsgemeinschaft\b|\bÜ?BAG\b'
    )
    corp_sfix = regex(r'\bMVZ\b|\bZMV\b')
    pform_abbr = {
        'MVZ': 'MVZ',
        'ZMV': 'MVZ',
        'ÜBAG': 'ÜBAG',
        'Überörtl. Berufsausübungsgemeinschaft': 'ÜBAG',
        'BAG': 'BAG',
        'Berufsausübungsgemeinschaft': 'BAG'
    }

    def parse(self, response, **query):
        from json import loads

        data = loads(response.text.strip('();'))['Data']
        for entry in data['Records']:
            assoc_pfix = self.assoc_pfix.match(entry['ADR_NAME'])
            if assoc_pfix:
                prac_form = self.pform_abbr.get(
                    assoc_pfix.group()
                )

                members = entry['ADR_NAME'].splitlines()[1:]
                for name in members:
                    assocs = members.copy()
                    assocs.remove(name)
                    yield {
                        'Associates': '; '.join(assocs),
                        'Practice': entry['ADR_NAME'],
                        'Name': name,
                        'Practice Form': prac_form,
                        'Street': entry['STRASSE'],
                        'ZIP': entry['PLZ'],
                        'City': entry['ORT'],
                        'District': entry['STADTTEIL'],
                        'Phone': entry['TELEFON']
                    }
            else:
                corp_sfix = self.corp_sfix.match(entry['ADR_NAME'])
                if corp_sfix:
                    prac_form = self.pform_abbr.get(
                        corp_sfix.group()
                    )
                else:
                    prac_form = ''

                yield {
                    'Associates': '',
                    'Practice': entry['ADR_NAME'],
                    'Name': ' '.join(entry['ADR_NAME'].splitlines()),
                    'Practice Form': prac_form,
                    'Street': entry['STRASSE'],
                    'ZIP': entry['PLZ'],
                    'City': entry['ORT'],
                    'District': entry['STADTTEIL'],
                    'Phone': entry['TELEFON']
                }

        if data['hasMore'] == 'true':
            query['startIndex'] = str(int(query['startIndex']) + 10)
            yield FormRequest(
                url='https://info.kzvth.de/ZaSuche/GetZaPaged',
                method='GET',
                formdata=query,
                cb_kwargs=query
            )
