# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TripadvItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    attraction = scrapy.Field()

    user = scrapy.Field()
    rating = scrapy.Field()
    title = scrapy.Field()
    num_contributions = scrapy.Field()
    num_helpful = scrapy.Field()
    rev_text = scrapy.Field()
    mo_yr_posted = scrapy.Field()
    mo_yr_visited = scrapy.Field()