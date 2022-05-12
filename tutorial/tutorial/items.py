# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProjectItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    date_created_friendly = scrapy.Field()
    date_created_parsed = scrapy.Field()
    image = scrapy.Field()
    catagory = scrapy.Field()
    location = scrapy.Field()
    percentage_funded = scrapy.Field()
    amount_raised = scrapy.Field()
    amount_goal = scrapy.Field()
    description = scrapy.Field()
    date_url_discovered = scrapy.Field()

    organizers = scrapy.Field()
    beneficiaries = scrapy.Field()

    counts = scrapy.Field()
    velocity = scrapy.Field()

    updates = scrapy.Field()
    photos = scrapy.Field()
    comments = scrapy.Field()
    highest_donations = scrapy.Field()
    donations = scrapy.Field()

class OrganizerItem(scrapy.Item):
    name = scrapy.Field()
    content = scrapy.Field()
