# -*- coding: utf-8 -*-
from scrapy import Spider


class BitdefenderStar(Spider):
    name = 'bitdefender_star'

    def __init__(self):
        super().__init__()

        with open(f'Antivirus/static_data/start_urls/bitdefender.txt') as start_urls:
            self.start_urls = list(start_urls)

    def parse(self, response):
        pass
