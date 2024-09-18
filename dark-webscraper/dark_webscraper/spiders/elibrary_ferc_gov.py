from scrapy import Spider
from scrapy.http import JsonRequest
from datetime import datetime, timezone


today = datetime.today()


class ElibraryFercGov(Spider):
    name = 'elibrary.ferc.gov'
    allowed_domains = ['elibrary.ferc.gov']

    query = {
        'accessionNumber': None,
        'affiliations': [],
        'allDates': False,
        'availability': None,
        'categories': [],
        'classTypes': [],
        'curPage': 1,
        'dateSearches': [
            {
             'DateType': 'filed_date',
             'startDate': today.replace(
                 month=today.month-2
             ).strftime('%m-%d-%Y'),
             'endDate': today.strftime('%m-%d-%Y')
            }
        ],
        'docketSearches': [
            {
             'docketNumber': '',
             'subDocketNumbers': []
            }
        ],
        'eFiling': False,
        'groupBy': 'NONE',
        'idolResultID': None,
        'libraries': [],
        'resultsPerPage': 200,
        'searchDescription': True,
        'searchFullText': True,
        'searchText': '*',
        'sortBy': "category"
    }

    def start_requests(self):
        yield JsonRequest(
            url='https://elibrary.ferc.gov'
                '/eLibraryWebAPI/api/Search/AdvancedSearch',
            data=self.query,
            callback=self.parse_first_page
        )

    def parse_first_page(self, response):
        res_time = datetime.strptime(
            str(response.headers.get('Date'), encoding='utf-8'),
            '%a, %d %b %Y %H:%M:%S %Z'
        ).astimezone(timezone.utc).isoformat()
        data = response.json()
        for item in data['searchHits']:
            yield {
                'url': 'https://elibrary.ferc.gov/eLibrary/search',
                'content': 'Regulatory',
                'website_name': 'Federal Energy Regulatory Commission (FERC)',
                'post_num': item['documentId'],
                'date_of_scrap': res_time,
                'text': item['description'],
                'timestamp': datetime.strptime(
                    item['filedDate'], '%m/%d/%Y'
                ).astimezone(timezone.utc).isoformat(),
                'extradata': {
                    'category': item['category'],
                    'class': item['classTypes'][0]['documentClass'],
                    'type': item['classTypes'][0]['documentType'],
                    'posted_on': item['postedDate'],
                    'docket_num': item['docketNumbers'] if item['docketNumbers'] else '',
                    'acession_num': item['acesssionNumber']
                }
            }

        from math import ceil
        for pnum in range(
            2, ceil(data['totalHits'] / data['numHits']) + 1
        ):
            self.query['curPage'] = pnum
            yield JsonRequest(
                url='https://elibrary.ferc.gov'
                    '/eLibraryWebAPI/api/Search/AdvancedSearch',
                data=self.query,
                callback=self.parse_page
            )

    def parse_page(self, response):
        res_time = datetime.strptime(
            str(response.headers.get('Date'), encoding='utf-8'),
            '%a, %d %b %Y %H:%M:%S %Z'
        ).astimezone(timezone.utc).isoformat()
        data = response.json()
        for item in data['searchHits']:
            yield {
                'url': 'https://elibrary.ferc.gov/eLibrary/search',
                'content': 'Regulatory',
                'website_name': 'Federal Energy Regulatory Commission (FERC)',
                'post_num': item['documentId'],
                'date_of_scrap': res_time,
                'text': item['description'],
                'timestamp': datetime.strptime(
                    item['filedDate'], '%m/%d/%Y'
                ).astimezone(timezone.utc).isoformat(),
                'extradata': {
                    'category': item['category'],
                    'class': item['classTypes'][0]['documentClass'],
                    'type': item['classTypes'][0]['documentType'],
                    'posted_on': item['postedDate'],
                    'docket_num': item['docketNumbers'] if item['docketNumbers'] else '',
                    'acession_num': item['acesssionNumber']
                }
            }
