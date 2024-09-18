from scrapy import Spider
from scrapy.http import FormRequest


class OcrportalHhsGov(Spider):
    name = 'ocrportal.hhs.gov'
    allowed_domains = ['ocrportal.hhs.gov']
    start_urls = ['https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf']

    def __init__(self, output, *args, **kwargs):
        from os.path import dirname, isdir
        if not isdir(dirname(output)):
            raise ValueError('Output destination non-existent.')
        self.output = output

    def parse(self, response):
        yield FormRequest.from_response(
            response,
            formid='ocrForm',
            formdata={
                'ocrForm:j_idt364': 'ocrForm:j_idt364'
            },
            dont_click=True,
            callback=self.save_table
        )

    def save_table(self, response):
        with open(self.output, mode='x', encoding='utf-8') as f:
            f.write(response.text)
