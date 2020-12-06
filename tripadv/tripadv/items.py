# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TripadvItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    url = scrapy.Field()

    attraction_city = scrapy.Field()
    attraction = scrapy.Field()

    user = scrapy.Field()
    user_loc = scrapy.Field()
    rating = scrapy.Field()
    rev_title = scrapy.Field()
    num_contributions_user = scrapy.Field()
    num_helpful_user = scrapy.Field()
    rev_text = scrapy.Field()
    mo_yr_posted = scrapy.Field()
    mo_yr_visited = scrapy.Field()
    num_helpful_votes = scrapy.Field()

    # item['attraction_city'] = response.meta['attraction_city']
    #         item['attraction'] = response.meta['attraction']

    #         item['user'] = user
    #         item['user_city'] = user_city
    #         item['rating'] = rating
    #         item['rev_title'] = rev_title
    #         item['num_contributions_user'] = num_contributions_user
    #         item['num_helpful'] = num_helpful
    #         item['rev_text'] = rev_text
    #         item['mo_yr_posted'] = mo_yr_posted
    #         item['mo_yr_visited'] = mo_yr_visited
    #         item['num_helpful_rev'] = num_helpful_rev