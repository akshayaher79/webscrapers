# Defined here is the main model of the scraped records.
# Make sure to go through this to grip the abbreviated/slang
# naming. Using this is mandatory.

# Low-down of basic usage: return an instance of the Agent class below from your
# parse methods. It works exactly like a dictionary. Eg:
# from ..items import Agent # The two dots before items are required.
# ...
# agent = Agent() # in parse method
# agent["name"] = "James Bond"
# ...
# return agent

# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Agent(scrapy.Item):

    # Profile page
    URL = scrapy.Field() # URL that was used in the request for the profile
                         # page (value of property response.request.url).
    DP_URL  = scrapy.Field()  # URL of the agent's picture displayed on the
                              # profile page.

    # Contact info
    name      = scrapy.Field()
    phone     = scrapy.Field() # Make sure to extract only one
    phone_alt = scrapy.Field() # phone number in one column and
    email     = scrapy.Field() # so with the emails.
    email_alt = scrapy.Field()

    # Online presence
    website   = scrapy.Field()
    twitter   = scrapy.Field()
    facebook  = scrapy.Field()
    linkedin  = scrapy.Field()
    instagram = scrapy.Field()
    yelp      = scrapy.Field()

    # Workplace info
    brand    = scrapy.Field() # If these turn out inseperable during scraping,
    branch   = scrapy.Field() # defer separation for the post stage.
    street   = scrapy.Field()
    city     = scrapy.Field()
    state    = scrapy.Field()
    ZIP      = scrapy.Field()
    work_tel = scrapy.Field()
    
    # Professional profile
    title     = scrapy.Field() # Position
    creds     = scrapy.Field() # Credentials
    firstyear = scrapy.Field() # First year of professional practice
    skills    = scrapy.Field() # Specialisations, experienced area
    turf      = scrapy.Field() # Areas of professional activity
    rating    = scrapy.Field()
    lang      = scrapy.Field() # Languages known to agent
    license   = scrapy.Field()
