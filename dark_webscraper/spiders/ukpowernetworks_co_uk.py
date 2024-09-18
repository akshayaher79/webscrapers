from scrapy import Spider


class UkpowernetworksCoUkSpider(Spider):
    name = 'ukpowernetworks.co.uk'
    allowed_domains = ['ukpowernetworks.co.uk']
    start_urls = ['https://www.ukpowernetworks.co.uk/power-cut/list']

    def parse(self, response):
        table_rows = response.css('tbody tr')
        for row in table_rows:
            type = row.xpath(
                '//td[@class="powercut-list__icon-list"]/text()[normalize-space()]'
                ).get()
            if type:
                type = type.strip()

            effected_postcode = row.css(
                '.powercut-list__affected-postcodes-list::text'
                ).get()
            if effected_postcode:
                effected_postcode = effected_postcode.strip()

            more_info = list(dict.fromkeys(row.css(
                'div.powercut-list__reason-info p::text'
                ).getall()))

            customer_aff = row.css(
                'td.powercut-list__customers-affected-list::text'
                ).get()
            if customer_aff:
                customer_aff = customer_aff.strip()

            reference = row.css(
                'div.powercut-list__incident-ref::text'
                ).get()
            if reference:
                reference = reference.strip()

            ref_url = row.css(
                'a.powercut-list__map-link::attr(href)'
                ).get()
            if ref_url:
                ref_url = ref_url.strip()

            report_time = row.css(
                'div.powercut-list__reason-info p:last-child::text'
                ).get()
            if report_time:
                report_time = report_time.strip()

            yield {
                'Type': type,
                'Effected_Postcode': effected_postcode,
                'More_Information': ' | '.join(more_info),
                'Customers_Effected': customer_aff,
                'Reference': reference,
                'Reference_URL': ref_url,
                'Report_Time': report_time

            }
