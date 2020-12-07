
from scrapy import Spider, Request
from tripadv.items import TripadvItem

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.action_chains import ActionChains

import time
import re

        # scrapy crawl tripadv_spider

class TripadvSpider(Spider):
    name = "tripadv_spider"

    # custom setting to allow for spider to crawl duplicate urls
        # parse_attractions_page crawls along the review_page_1st_urls of parse_attractions.
        # bc of this, it does not crawl the 1st url of result_urls (or the redirect page without url insertion)
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    allowed_urls = ['https://www.tripadvisor.com']
    
    start_urls = [
        'https://www.tripadvisor.com/Attractions-g60745-Activities-Boston_Massachusetts.html',
        # 'https://www.tripadvisor.com/Attractions-g32655-Activities-Los_Angeles_California.html',
        # 'https://www.tripadvisor.com/Attractions-g60763-Activities-New_York_City_New_York.html',
        # 'https://www.tripadvisor.com/Attractions-g35805-Activities-Chicago_Illinois.html',
        ]

    
    def start_requests(self):
        for start_url in self.start_urls:
            yield Request(url=start_url, callback=self.parse_attractions)


    def parse_attractions(self, response):

        # BOS' TripAdvisor page is set up differently than LAX, NYC, ORD
            # therefore, we need if statement to treat the xpath on the pages differently
        if response.url == self.start_urls[0]:
            
            # get the partial urls for the reviews of the top 10 attractions
                # once again, Boston's setup is different
                # we have to use a stepwise function to skip the urls ending in '#REVIEWS' so that we
                # do not have to account for those urls in parse_attractions_page's result_urls
            attrctn_to_rvw = response.xpath('//div[@class="_20eVZLwe"]/div/a/@href').extract()[0:1:2]
           
            # add the partial urls to the root url for the full url for each attraction review page
            review_page_1st_urls = [self.allowed_urls[0] + partial for partial in attrctn_to_rvw]
        
        else:
            
            # get the partial urls for the reviews of the top 10 attractions
            attrctn_to_rvw = response.xpath('//a[@class="_255i5rcQ"]/@href').extract()[:1]
                # results in:
                # ['/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html']
            
            # add the partial urls to the root url for the full url for each attraction review page
            review_page_1st_urls = [self.allowed_urls[0] + partial for partial in attrctn_to_rvw]
            # results in:
            # ['www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html']

        for rev_url in review_page_1st_urls:
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

        result_urls = [f'Reviews-or{(i-1)*5}-'.join(response.url.split('Reviews-'))+'#REVIEWS' for i in range(2,3)] # range(2,3)
        result_urls.insert(0, response.url+'#REVIEWS')
        # results in:
        # ['www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html#REVIEWS',
        # 'www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-or5-The_Getty_Center-Los_Angeles_California.html#REVIEWS',
        # 'www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-or10-The_Getty_Center-Los_Angeles_California.html#REVIEWS']

        meta = {'attraction_city': attraction_city,
                'attraction': attraction}

        for pg_url in result_urls:
            yield Request(url = pg_url, callback = self.parse_review_pages, meta=meta)


    # scrapy crawl tripadv_spider

    def parse_review_pages(self, response):
        reviews = response.xpath('.//div[@class="Dq9MAugU T870kzTX LnVzGwUB"]')
        
        # use Selenium to switch to active browser
        driver = webdriver.Chrome(r'C:\Users\tdcho\OneDrive\Desktop\NYCDSA\chromedriver.exe')
        driver.get(response.url)
        driver.maximize_window()
        WebDriverWait(driver, 10)
        driver.switch_to.active_element

        # use selenium to click on 1st 'read more' element as that expands all other review texts
        readmore = driver.find_element_by_xpath('//span[@class="_3maEfNCR"]')
        readmore.click()
        # Slows down the text expansion so the text can be scraped
        time.sleep(.5)

        wait_review = WebDriverWait(driver, 10)
        # selenium_reviews = wait_review.until(EC.presence_of_all_elements_located((By.XPATH, './/div[@data-test-target="reviews-tab"]')))

        selenium_reviews = wait_review.until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="Dq9MAugU T870kzTX LnVzGwUB"]')))
        # for selenium_review in selenium_reviews:
        #     rev_text = selenium_review.find_element_by_xpath('.//q[@class="IRsGHoPm"]').text

        # driver.quit()

        for selenium_review, review in zip(selenium_reviews, reviews):
            
            rev_text = selenium_review.find_element_by_xpath('.//q[@class="IRsGHoPm"]').text

            user = review.xpath('.//a[@class="ui_header_link _1r_My98y"]/text()').extract_first()
            mo_yr_posted = review.xpath('.//div[@class="_2fxQ4TOx"]/span/text()').extract_first().split("review ")[1].strip()
            user_loc = review.xpath('.//span[@class="default _3J15flPT small"]/text()').extract_first()   
            num_contributions_user = review.xpath('.//span[@class="_1fk70GUn"]/text()').extract()[0]
            
            try: 
                num_helpful_user = review.xpath('.//span[@class="_1fk70GUn"]/text()').extract()[1]
                num_helpful_user = int(re.findall('\d+', num_helpful_user)[0])
            except Exception as e:
                print(type(e), e)
                num_helpful_user = 0
            
            rating = int(review.xpath('.//div[@data-test-target="review-rating"]//span/@class').extract_first().split(' bubble_')[1].strip('0') or '0')
            rev_title = review.xpath('.//div[@data-test-target="review-title"]//span/text()').extract_first()

        # scrapy crawl tripadv_spider
            # rev_text = selenium_review.find_element_by_xpath('.//q[@class="IRsGHoPm"]').text

            # selenium_review = wait_review.until(EC.presence_of_all_elements_located((By.XPATH,
            #                         './/div[@class="Dq9MAugU T870kzTX LnVzGwUB"]')))
            # for selenium_review in selenium_reviews:
            #     rev_text = selenium_review.find_element_by_xpath('.//q[@class="IRsGHoPm"]').text

            mo_yr_visited = review.xpath('.//span[@class="_34Xs-BQm"]/text()').extract_first().strip()
            
            try: 
                num_helpful_votes = review.xpath('.//span[@class="_3kbymg8R _2o1bmw1O"]/text()').extract_first()
                num_helpful_votes = int(re.findall('\d+', num_helpful_votes)[0])
            except Exception as e:
                print(type(e), e)
                num_helpful_votes = 0

            item = TripadvItem()

            item['attraction_city'] = response.meta['attraction_city']
            item['attraction'] = response.meta['attraction']

            item['user'] = user
            item['user_loc'] = user_loc
            item['rating'] = rating
            item['rev_title'] = rev_title
            item['num_contributions_user'] = num_contributions_user
            item['num_helpful_user'] = num_helpful_user
            item['rev_text'] = rev_text
            item['mo_yr_posted'] = mo_yr_posted
            item['mo_yr_visited'] = mo_yr_visited
            item['num_helpful_votes'] = num_helpful_votes

            yield item
            
        driver.quit()