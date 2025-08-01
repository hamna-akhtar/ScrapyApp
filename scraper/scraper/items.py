# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AdItem(scrapy.Item):
    url = scrapy.Field()
    city = scrapy.Field()
    postal_code = scrapy.Field()
    country = scrapy.Field()
    address = scrapy.Field()
    rooms = scrapy.Field()
    surface = scrapy.Field()
    price = scrapy.Field()
    website = scrapy.Field()
    scraped_at = scrapy.Field()
    bedrooms = scrapy.Field()
    balcony = scrapy.Field()
    garden = scrapy.Field()
    bath = scrapy.Field()
    furnished = scrapy.Field()
    sharing = scrapy.Field()
    pet_friendly = scrapy.Field()
    income_requirement = scrapy.Field()
    students = scrapy.Field()
    # senior_home = scrapy.Field()
    description = scrapy.Field()
    photo = scrapy.Field()
    realtor = scrapy.Field()
    realtor_link = scrapy.Field()