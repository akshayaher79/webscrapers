from scrapy import Spider
from datetime import timedelta, timezone, datetime


class CrackedTo(Spider):
    name = 'cracked.to'
    allowed_domains = ['cracked.to']
    start_urls = ['https://cracked.to']

    custom_settings = {
        'DOWNLOAD_DELAY': 7,
        'CONCURRENT_REQUESTS': 1,
        'ITEM_PIPELINES': {}
    }

    def parse(self, response):
        yield from response.follow_all(
            css='a.largetext[href^="Forum"]',
            callback=self.parse_forum
        )

    def parse_forum(self, response):
        forum = response.css('.fd-bg > h1::text').get()
        yield from response.follow_all(
            css='.forum a.largetext',
            callback=self.parse_subforum,
            cb_kwargs={'forum': forum}
        )

    def parse_subforum(self, response, forum):
        subforum = response.css('.fd-bg > h1::text').get()
        yield from response.follow_all(
            css='#topiclist > tr > td[width="65%"] a[href^="Thread"]',
            callback=self.parse_thread,
            cb_kwargs={'forum': forum, 'subforum': subforum}
        )
        next = response.css('a.pagination_next')
        if next:
            yield response.follow(
                url=next[0],
                callback=self.parse_subforum,
                cb_kwargs={'forum': forum}
            )

    def parse_thread(self, response, forum, subforum):
        res_time = datetime.strptime(
            str(response.headers.get('Date'), encoding='utf-8'),
            '%a, %d %b %Y %H:%M:%S %Z'
        )

        op_title = response.css('.thread-header > h1::text').get()
        op_id = response.css('#posts > div:first-child > a::attr(id)').get()

        op_date = response.css(
            '#posts > div:first-child .post-box '
            '.post_date > span:last-child::text'
        ).get()
        if op_date.endswith('ago'):
            op_date = op_date.split()
            unit = op_date[-2]
            duration = int(op_date[-3])
            op_date = res_time - timedelta(**{unit: duration})
        else:
            op_date = datetime.strptime(
                f'{op_date} -0700', '%d %B, %Y - %I:%M %p %z'
            )

        op_text = response.css(
            '#posts > div:first-child .post-content .post_body'
        ).xpath('normalize-space()').get()
        views = response.css('.thread_views::text').get().strip()
        op_user = response.css(
            '.thread-header > .smalltext > a::text'
        ).get()

        yield {
            'website_name': 'cracked.to',
            'url': f'{response.request.url}#{op_id}',
            'timestamp': op_date.astimezone(timezone.utc).isoformat(),
            'text': op_text,
            'post_num': '#1',
            'date_of_scrap': res_time.astimezone(timezone.utc).isoformat(),
            'content': 'Forum',
            'extradata': {
                'threads_subject': op_title,
                'views': views,
                'user': op_user,
                'forum': forum,
                'subforum': subforum
            }
        }

        for reply in response.css('#posts > div')[1:]:
            re_date = reply.css(
                '.post-box .post_date > span:last-child::text'
            ).get()
            if re_date.endswith('ago'):
                re_date = re_date.split()
                unit = re_date[-2]
                duration = int(re_date[-3])
                re_date = res_time - timedelta(**{unit: duration})
            else:
                re_date = datetime.strptime(
                    f'{re_date} -0700', '%d %B, %Y - %I:%M %p %z'
                )

            re_id = reply.css('a::attr(id)').get()
            re_text = reply.css(
                '.post-content .post_body'
            ).xpath('normalize-space()').get()
            re_index = reply.css('.post-head .posturl a::text').get()
            re_user = reply.css(
                'a[data-class="profile_url"]::text'
            ).get()

            yield {
                'website_name': 'cracked.to',
                'url': f'{response.request.url}#{re_id}',
                'timestamp': re_date.astimezone(timezone.utc).isoformat(),
                'text': re_text,
                'post_num': re_index,
                'date_of_scrap': res_time.astimezone(timezone.utc).isoformat(),
                'content': 'Forum',
                'extradata': {
                    'threads_subject': op_title,
                    'views': views,
                    'user': re_user,
                    'forum': forum,
                    'subforum': subforum
                }
            }

        next = response.css('a.pagination_next')
        if next:
            yield response.follow(
                url=next[0],
                callback=self.parse_thread_tail,
                cb_kwargs={
                    'forum': forum, 'subforum': subforum,
                    'op_id': op_id, 'op_title': op_title,
                    'views': views
                }
            )

    def parse_thread_tail(self, response, **kwargs):
        res_time = datetime.strptime(
            str(response.headers.get('Date'), encoding='utf-8'),
            '%a, %d %b %Y %H:%M:%S %Z'
        )
        for reply in response.css('#posts > div'):
            re_date = reply.css(
                '.post-box .post_date > span:last-child::text'
            ).get()
            if re_date.endswith('ago'):
                re_date = re_date.split()
                unit = re_date[-2]
                duration = int(re_date[-3])
                re_date = res_time - timedelta(**{unit: duration})
            else:
                re_date = datetime.strptime(
                    f'{re_date} -0700', '%d %B, %Y - %I:%M %p %z'
                )

            re_id = reply.css('a::attr(id)').get()
            re_text = reply.css(
                '.post-content .post_body'
            ).xpath('normalize-space()').get()
            re_index = reply.css('.post-head .posturl a::text').get()
            re_user = reply.css(
                'a[data-class="profile_url"]::text'
            ).get()

            yield {
                'website_name': 'cracked.to',
                'url': f'{response.request.url}#{re_id}',
                'timestamp': re_date.astimezone(timezone.utc).isoformat(),
                'text': re_text,
                'post_num': re_index,
                'date_of_scrap': res_time.astimezone(timezone.utc).isoformat(),
                'content': 'Forum',
                'extradata': {
                    'threads_subject': kwargs["op_title"],
                    'views': kwargs["views"],
                    'user': re_user,
                    'forum': kwargs['forum'],
                    'subforum': kwargs['subforum']
                }
            }

        next = response.css('a.pagination_next')
        if next:
            yield response.follow(
                url=next[0],
                callback=self.parse_thread_tail,
                cb_kwargs=kwargs
            )
