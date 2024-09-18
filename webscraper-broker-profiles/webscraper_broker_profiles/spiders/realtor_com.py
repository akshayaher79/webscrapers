from scrapy import Request, Spider
from ..items import Agent
from pkg_resources import resource_stream
from json import loads as jsonparse


class RealtorCom(Spider):
    """
    Searches the whole site for realtors in each area in the US ZIP
    postal system and extracts details from their profile pages. Also
    crawls SERPs of the website's search engine whose URLs are listed
    in the start URLs file.

    Spider parameters
    =================

    start_urls_f
    ------------
    Path to a text file containing start URLs.

    profile_urls_f
    ------------
    Path to a text file containing URLs of agent profile pages that aren't
    crawled to by the spider.
    """

    name = 'realtor.com'
    allowed_domains = ['realtor.com']

    custom_settings = {
        'ITEM_PIPELINES': {
            'brokerage_info_crawler.pipelines.NameCleaner': 300,
            'brokerage_info_crawler.pipelines.CityCleaner': 301,
            'brokerage_info_crawler.pipelines.NumberCleaner': 302
        }
    }

    def __init__(self, start_urls_f=None, profile_urls_f=None):
        if start_urls_f:
            with open(start_urls_f) as start_urls:
                self.start_urls = list(start_urls)
        if profile_urls_f:
            with open(profile_urls_f) as profile_urls:
                self.profile_urls = list(profile_urls)

        super().__init__()

    def start_requests(self):
        yield from super().start_requests()

        for url in self.profile_urls:
            yield Request(url, callback=self.parse_profile)

        with resource_stream(
            'brokerage_info_crawler.static_data', 'ZIPs.txt'
        ) as zips:
            for zip_ in zips:
                zip_ = str(zip_, encoding='utf-8').rstrip()
                yield Request(f'https://realtor.com/realestateagents/{zip_}')

    def parse(self, response):
        yield from response.follow_all(
            css='#agent_list_wrapper div.agent-list-card-img-wrapper a',
            callback=self.parse_profile
        )

        next = response.css('div.paginatorWrapper a[rel="next"]')
        if next:
            yield response.follow(next[0])

    def parse_profile(self, response):
        data = jsonparse(
            response.css('#__NEXT_DATA__::text').get(
            ).replace(r'\"', "'").replace('\\', '\\\\')
        )
        agent_details = data['props']['pageProps']['agentDetails']
        agent = Agent()

        # Identity and contact details
        # agent['DP_URL'] = agent_details['photo']['href']
        # agent['URL'] = response.request.url

        if 'full_name' in agent_details:
            agent['name'] = agent_details['full_name']
        elif 'person_name' in agent_details:
            agent['name'] = agent_details['person_name']
        else:
            agent['name'] = agent_details['name']

        agent['title'] = agent_details.get('title')

        for phone in agent_details['phones']:
            if phone['type'] == 'Mobile':
                agent['phone'] = phone['number']
            elif phone['type'] == 'Office':
                agent['work_tel'] = phone['number']
            else:
                agent["phone_alt"] = phone['number']

        # agent['email'] = agent_details.get('email')
        #
        # # Social media IDs and pages
        # agent['website'] = agent_details.get('href')
        # # try:
        #     agent['facebook'] = data['props']['initialReduxState']['profile']
        #     ['profileData']['social_connections']['facebook']['pages'][0]['link']
        # except KeyError:
        #     pass
        # try:
        #     agent['twitter'] = data['props']['initialReduxState']['profile']
        #     ['profileData']['social_connections']['twitter']['link']
        # except KeyError:
        #     pass
        #
        # # Practice details
        # agent['turf'] = '; '.join(
        #     area['name'] + ', ' + area['state_code'] for area in
        #     agent_details['served_areas']
        # )
        # agent['skills'] = '; '.join(
        #     spec['name'] for spec in
        #     agent_details['specializations']
        # )
        # agent['firstyear'] = agent_details.get('first_year')
        # agent['lang'] = '; '.join(agent_details.get('languages') or [])

        # Office details
        agent['brand'] = agent_details['broker']['name']
        agent['street'] = agent_details['address']['line']
        agent['city'] = agent_details['address']['city']
        agent['state'] = agent_details['address']['state_code']
        agent['ZIP'] = agent_details['address']['postal_code']

        return agent
