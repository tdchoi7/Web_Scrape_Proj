# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TripadvItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    attraction_city = scrapy.Field()
    attraction = scrapy.Field()

    user = scrapy.Field()
    user_loc = scrapy.Field()
    rating = scrapy.Field()
    rev_title = scrapy.Field()
    num_contributions_user = scrapy.Field()
    num_helpful_user = scrapy.Field()
    rev_text = scrapy.Field()
    mo_yr_posted_final = scrapy.Field()
    mo_yr_visited = scrapy.Field()
    num_helpful_votes = scrapy.Field()