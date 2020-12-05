
from scrapy import Spider, Request
from tripadv.items import TripadvItem
import re

# scrapy crawl tripadv_spider

class TripadvSpider(Spider):
    name = "tripadv_spider"
    allowed_urls = ['https://www.tripadvisor.com']


    def start_requests(self):
        city_urls = [
        # 'https://www.tripadvisor.com/Attractions-g60745-Activities-Boston_Massachusetts.html',
        'https://www.tripadvisor.com/Attractions-g32655-Activities-Los_Angeles_California.html',
        # 'https://www.tripadvisor.com/Attractions-g60763-Activities-New_York_City_New_York.html',
        # 'https://www.tripadvisor.com/Attractions-g35805-Activities-Chicago_Illinois.html',
        ]

        for url in city_urls:
            yield Request(url=url, callback=self.parse_attractions)

    def parse_attractions(self, response):
        # BOS' TripAdvisor page is set up differently than LAX, NYC, ORD
            # therefore, we need if statement to parse the pages differently
        if response.url == 'https://www.tripadvisor.com/Attractions-g60745-Activities-Boston_Massachusetts.html':
            # get the partial urls for the reviews of the top 10 attractions
            # attraction_city = response.xpath('//div[@class="_24Bn3Gzx"]/h2/span/text()').extract().split()[3:]
            # attraction = response.xpath('//div[@class="_20eVZLwe"]/div/a/h3/text()').extract()[:2]
            attrctn_to_rvw = response.xpath('//div[@class="F1FRMVtv"]/span/a/@href').extract_first()[:3]
            # add the partial urls to the root url for the full url for each attraction review page
            review_page = [self.allowed_urls[0] + partial for partial in attrctn_to_rvw]
        else:
            # get the partial urls for the reviews of the top 10 attractions
            # attraction_city = response.xpath('//h2[@class="_3YVWnI89"]/text()').extract_first()[3:]
            attrctn_to_rvw = response.xpath('//a[@class="_255i5rcQ"]/@href').extract()[:3]
                # results in:
                # ['/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html',
                #  '/Attraction_Review-g32655-d116887-Reviews-Griffith_Observatory-Los_Angeles_California.html',
                #  '/Attraction_Review-g32655-d104417-Reviews-Universal_Studios_Hollywood-Los_Angeles_California.html']
            # add the partial urls to the root url for the full url for each attraction review page
            review_page = [self.allowed_urls[0] + partial for partial in attrctn_to_rvw]
            # results in:
            # ['www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html',
            #  'www.tripadvisor.com/Attraction_Review-g32655-d116887-Reviews-Griffith_Observatory-Los_Angeles_California.html',
            #  'www.tripadvisor.com/Attraction_Review-g32655-d104417-Reviews-Universal_Studios_Hollywood-Los_Angeles_California.html']

        # print('=='*25)
        # print(review_page)
        # print('=='*25)

        for url in review_page:
            yield Request(url=url, callback=self.parse_attractions_page)


    def parse_attractions_page(self, response):
        attraction = response.xpath('//h1[@class="ui_header h1"]/text()').extract_first()
        attraction_city = ' '.join(response.xpath('//div[@class="eQSJNhO6"]/span/a/text()').extract_first().split()[4:])
        num_pages = int(response.xpath('//a[@class="pageNum "]/text()').extract()[-1])

        review_pg_url = [f'Reviews-or{(i-1)*5}-'.join(response.url.split('Reviews-'))+'#REVIEWS' for i in range(1, 3)]

        # attraction_link = response.xpath('//a[@class="_255i5rcQ"]/@href').extract()

        meta = {'attraction_city': attraction_city,
                'attraction': attraction}

        # print('=='*25)
        # # print(review_pg_url)
        # print(attraction, attraction_city)
        # print('**'*25)
        # print(review_pg_url)
        # print('=='*25)

        for url in review_pg_url:
            yield Request(url=url, callback=self.parse_review_page, meta=meta)


    def parse_review_page(self, response):
        reviews = response.xpath('//div[@class="Dq9MAugU T870kzTX LnVzGwUB"]')

        for review in reviews:
            user = review.xpath('//a[@class="ui_header_link _1r_My98y"]/text()').extract_first()
            mo_yr_posted = review.xpath('.//div[@class="_2fxQ4TOx"]/span/text()').extract_first().split("review ")[1].strip()
            num_contributions_user = response.xpath('//span[@class="_1fk70GUn"]/text()').extract()[0]
            num_helpful_user = review.xpath('//span[@class="_1fk70GUn"]/text()').extract()[1]
            
            rating = int(review.xpath('//div[@data-test-target="review-rating"]//span/@class').extract_first().split(' bubble_')[1].strip('0') or '0')
            rev_title = review.xpath('//div[@data-test-target="review-title"]//span/text()').extract_first()
            # no need for readmore button bc xpath gives us 2 blocks of text: 1st w/o read more 2nd w/ readmore
            rev_text = re.sub(' +', ' ', ' '.join(review.xpath('//q[@class="IRsGHoPm"]//text()').extract()[:2]))
            
            mo_yr_visited = review.xpath('//span[@class="_34Xs-BQm"]/text()').extract_first().strip()
            num_helpful_rev = response.xpath('//span[@class="_3kbymg8R _2o1bmw1O"]/text()').extract_first()
            num_helpful_rev = int(re.findall('\d+', num_helpful_rev)[0])

            item = TripadvItem()
            item['attraction_city'] = response.meta['attraction_city']
            item['attraction'] = response.meta['attraction']

            item['user'] = user
            item['user_city'] = user_city
            item['rating'] = rating
            item['rev_title'] = rev_title
            item['num_contributions_user'] = num_contributions_user
            item['num_helpful'] = num_helpful
            item['rev_text'] = rev_text
            item['mo_yr_posted'] = mo_yr_posted
            item['mo_yr_visited'] = mo_yr_visited
            item['num_helpful_rev'] = num_helpful_rev

            yield item


        # to visit the links that we have scraped
        for index, url in enumerate(attrctn_rvw_urls):
            yield Request(url=url, callback=self.parse_results_page, meta=meta)


 #    def parse_results_page(self, response):
 #        # from:
 #        # 'https://www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html'

 #        num_pages = int(response.xpath('//a[@class="pageNum "]/text()').extract()[-1])

 #        # page_grouping = re.search('/Attraction_Review-g(\d+)-d(\d+)-Reviews-([\W\S]+).html#REVIEWS', attrctn_rvw_urls[:3])
 #        # city_num, attr_loc_num, attrctn_name = int(page_grouping.group(1)), int(page_grouping.group(2)), page_grouping.group(3)

 #        # the webpage numbering seems to go by the number of the last review of the previous page starting with '-or0' and a 2nd page '-or5'
 #            # with 5 reviews per page, we would have to multiply the previous page number by 5 to get the correct webpage address
 #        rev_page_urls = [f'{allowed_urls[0]}/Attraction_Review-g{city_num}-d{attr_loc_num}-Reviews-or{(i-1)*5}-{attrctn_name}.html#REVIEWS' for i in range(1, num_pages)]

 #        print('=='*25)
 #        print(len(rev_page_urls))
 #        print('=='*25)

        # for url in rev_page_urls:
        #     yield Request(url=url, callback = self.parse_reviews)


    # def parse_reviews(self, response):
    #    
    # city = scrapy.Field()
    # attraction = scrapy.Field()

    # user = scrapy.Field()
    # rating = scrapy.Field()
    # rev_title = scrapy.Field()
    # num_contributions_user = scrapy.Field()
    # num_helpful_user = scrapy.Field()
    # rev_text = scrapy.Field()
    # mo_yr_posted = scrapy.Field()
    # mo_yr_visited = scrapy.Field()
    # num_helpful_rev = scrapy.Field()

        # date_posted_text = response.xpath('.//div[@class="_2fxQ4TOx"]/span/text()').extract()
        # grouped = re.search('wrote a review (... \d+)', date_posted_text)
        # dates_posted = grouped.group(0)



        # for url in page_urls:
        #   # if page 
        #   yield Request(url=url, callback=self.parse_page_urls)

