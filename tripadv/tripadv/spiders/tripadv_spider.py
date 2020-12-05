
from scrapy import Spider, Request
from tripadv.items import TripadvItem
import re

        # scrapy crawl tripadv_spider

class TripadvSpider(Spider):
    name = "tripadv_spider"
    allowed_urls = ['https://www.tripadvisor.com']


    def start_requests(self):
        start_urls = [
        # 'https://www.tripadvisor.com/Attractions-g60745-Activities-Boston_Massachusetts.html',
        'https://www.tripadvisor.com/Attractions-g32655-Activities-Los_Angeles_California.html',
        # 'https://www.tripadvisor.com/Attractions-g60763-Activities-New_York_City_New_York.html',
        # 'https://www.tripadvisor.com/Attractions-g35805-Activities-Chicago_Illinois.html',
        ]

        for url in start_urls:
            yield Request(url=url, callback=self.parse_attractions)

    def parse_attractions(self, response):
        # BOS' TripAdvisor page is set up differently than LAX, NYC, ORD
            # therefore, we need if statement to parse the pages differently
        if response.url == 'https://www.tripadvisor.com/Attractions-g60745-Activities-Boston_Massachusetts.html':
            # get the partial urls for the reviews of the top 10 attractions
            # attraction_city = response.xpath('//div[@class="_24Bn3Gzx"]/h2/span/text()').extract().split()[3:]
            # attraction = response.xpath('//div[@class="_20eVZLwe"]/div/a/h3/text()').extract()[:2]
            attrctn_to_rvw = response.xpath('//div[@class="F1FRMVtv"]/span/a/@href').extract_first()[:1]
            # add the partial urls to the root url for the full url for each attraction review page
            review_page = [self.allowed_urls[0] + partial for partial in attrctn_to_rvw]
        
        else:
            # get the partial urls for the reviews of the top 10 attractions
            # attraction_city = response.xpath('//h2[@class="_3YVWnI89"]/text()').extract_first()[3:]
            attrctn_to_rvw = response.xpath('//a[@class="_255i5rcQ"]/@href').extract()[:1]
                # results in:
                # ['/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html']
            
            # add the partial urls to the root url for the full url for each attraction review page
            review_page = [self.allowed_urls[0] + partial for partial in attrctn_to_rvw]
            # results in:
            # ['www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html']

        for rev_url in review_page:
            yield Request(url=rev_url, callback=self.parse_attractions_page)


    def parse_attractions_page(self, response):
        attraction = response.xpath('//h1[@class="ui_header h1"]/text()').extract_first()
        # results in:
        # 'The Getty Center'

        attraction_city = ' '.join(response.xpath('//div[@class="eQSJNhO6"]/span/a/text()').extract_first().split()[4:])
        # results in:
        # 'Los Angeles'
        
        # get number of pages to create list of urls for each review page
        num_pages = int(response.xpath('//a[@class="pageNum "]/text()').extract()[-1])
        # each page (starting from 0) has a '-or#' sequence after "Reviews" where the multiple of 5
        # indicates the number of the last review of the previous page
            # therefore, '-or0' is pg 1, '-or5' is pg 2, '-or10' is page 3, etc

        result_urls = [f'Reviews-or{(i-1)*5}-'.join(response.url.split('Reviews-'))+'#REVIEWS' for i in range(1,4)]
        result_urls[0] = response.url+'#REVIEWS'
        # results in:
        # ['www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html#REVIEWS',
        # 'www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-or5-The_Getty_Center-Los_Angeles_California.html#REVIEWS',
        # 'www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-or10-The_Getty_Center-Los_Angeles_California.html#REVIEWS']

        meta = {'attraction_city': attraction_city,
                'attraction': attraction}

        for pg_url in result_urls:
            # print(pg_url)
            yield Request(url = pg_url, callback = self.parse_review_pages, meta=meta)
            #should result in 3 pages of scraped reviews


    def parse_review_pages(self, response):
        reviews = response.xpath('.//div[@class="Dq9MAugU T870kzTX LnVzGwUB"]')
        
        # print('**'*25)
        # print(reviews[0])
        # print(reviews[1])
        # print(reviews[2])
        # print(reviews[3])
        # print(reviews[4])
        # print('**'*25)

        for review in reviews:
            user = review.xpath('.//a[@class="ui_header_link _1r_My98y"]/text()').extract_first()
            mo_yr_posted = review.xpath('.//div[@class="_2fxQ4TOx"]/span/text()').extract_first().split("review ")[1].strip()
            user_city = review.xpath('.//span[@class="default _3J15flPT small"]/text()').extract_first()
            num_contributions_user = review.xpath('.//span[@class="_1fk70GUn"]/text()').extract()[0]
            
            # need to correct this
            try: 
                num_helpful_user = review.xpath('.//span[@class="_1fk70GUn"]/text()').extract()[1]
                num_helpful_user = int(re.findall('\d+', num_helpful_user)[0])
            except Exception as e:
                print(type(e), e)
                q_and_a = 0
            
            rating = int(review.xpath('.//div[@data-test-target="review-rating"]//span/@class').extract_first().split(' bubble_')[1].strip('0') or '0')
            rev_title = review.xpath('.//div[@data-test-target="review-title"]//span/text()').extract_first()
            # no need for readmore button bc xpath gives us 2 blocks of text: 1st w/o read more 2nd w/ readmore
            rev_text = re.sub(' +', ' ', ' '.join(review.xpath('.//q[@class="IRsGHoPm"]//text()').extract()))
            
            mo_yr_visited = review.xpath('.//span[@class="_34Xs-BQm"]/text()').extract_first().strip()
            
            try: 
                num_helpful_votes = review.xpath('.//span[@class="_3kbymg8R _2o1bmw1O"]/text()').extract_first()
                num_helpful_votes = int(re.findall('\d+', num_helpful_votes)[0])
            except Exception as e:
                print(type(e), e)
                q_and_a = 0

            print('**'*25)
            print('**'*25)
            print(user)
            print(mo_yr_posted)
            print(user_city)
            print(num_contributions_user)
            print(num_helpful_user)
            print(rating)
            print(rev_title)
            print(rev_text)
            print(mo_yr_visited)
            print(num_helpful_votes)
            print('=='*25)
            print('=='*25)

            item = TripadvItem()
            item['attraction_city'] = response.meta['attraction_city']
            item['attraction'] = response.meta['attraction']

            item['user'] = user
            item['user_city'] = user_city
            item['rating'] = rating
            item['rev_title'] = rev_title
            item['num_contributions_user'] = num_contributions_user
            item['num_helpful_user'] = num_helpful_user
            item['rev_text'] = rev_text
            item['mo_yr_posted'] = mo_yr_posted
            item['mo_yr_visited'] = mo_yr_visited
            item['num_helpful_votes'] = num_helpful_votes

            yield item

            # print('=='*25)
            # print('=='*25)
            # print('**'*25)
            # print('**'*25)
            # print(user)
            # print('**'*25)
            # print('**'*25)
            # print('=='*25)
            # print('=='*25)

        # print('**END**'*10)