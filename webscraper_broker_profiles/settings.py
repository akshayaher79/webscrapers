# Scrapy settings for webscraper_broker_profiles project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'webscraper-broker-profiles'

SPIDER_MODULES = ['webscraper_broker_profiles.spiders']
NEWSPIDER_MODULE = 'webscraper_broker_profiles.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'webscraper_broker_profiles (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'webscraper_broker_profiles.middlewares.WebscraperBrokerProfilesSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'webscraper_broker_profiles.middlewares.WebscraperBrokerProfilesDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'webscraper_broker_profiles.pipelines.NameCleaner': 300,
    'webscraper_broker_profiles.pipelines.CityCleaner': 301,
    'webscraper_broker_profiles.pipelines.StateNameEncoder': 302,
    'webscraper_broker_profiles.pipelines.NumberCleaner': 303
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# Use 3rd party fake user-agent provider component
# from https://pypi.org/project/scrapy-fake-useragent/
FAKEUSERAGENT_PROVIDERS = [
    # this is the first provider we'll try
    'scrapy_fake_useragent.providers.FakeUserAgentProvider',
    # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
    'scrapy_fake_useragent.providers.FakerProvider',
    # fall back to USER_AGENT value
    'scrapy_fake_useragent.providers.FixedUserAgentProvider',
]
USER_AGENT = 'Mozilla/5.0 (X11; Linux; rv:74.0) Gecko/20100101 Firefox/74.0'

# Feed exports
FEEDS = {
    # Items flow right into the bucket, sorted by spider name and time.
    r'gs://bqpload/scrapy/%(name)s/%(time)s.csv': {
        'format': 'csv',
        'fields': [
            'URL', 'DP_URL', 'name', 'title', 'phone', 'phone_alt',
            'work_tel', 'email', 'email_alt', 'website', 'twitter',
            'facebook', 'brand', 'branch', 'street', 'city', 'state',
            'ZIP', 'work_XP', 'turf', 'skills'
        ]
    }
}

