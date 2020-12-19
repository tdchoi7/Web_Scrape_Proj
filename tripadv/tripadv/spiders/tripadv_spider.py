
from scrapy import Spider, Request
from scrapy.exceptions import CloseSpider
from tripadv.items import TripadvItem

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime
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
        'https://www.tripadvisor.com/Attractions-g32655-Activities-Los_Angeles_California.html',
        'https://www.tripadvisor.com/Attractions-g60763-Activities-New_York_City_New_York.html',
        'https://www.tripadvisor.com/Attractions-g35805-Activities-Chicago_Illinois.html',
        ]


    def get_mo_yr_posted(self, mo_yr_post):
        """
        Converts the scraped review posted date to:
        'month year' format
        """
        import calendar

        # grabs month and day/year
        mo_yr_post_group = re.search('(\S+) (\d+)', mo_yr_post)

        # converts 'Today' to current month and year
        if mo_yr_post == 'Today':
            today = datetime.now() 
            mo_yr_post = str(today.strftime('%h')) + ' ' + str(today.strftime('%Y'))
            return mo_yr_post

        # converts 'Yesterday' to yesterday's month and year
        elif mo_yr_post == 'Yesterday':
            today = datetime.now()

            # accounts for change in month if yesterday was a diff month
            if int(today.strftime('%d')) - 1 <= 0:
                monthinteger = int(today.strftime('%m')) - 1

                # accounts for change in year 
                if monthinteger == 0:
                    yearinteger = int(today.strftime('%Y')) - 1
                    mo_yr_post = calendar.month_abbr[monthinteger] + ' ' + str(yearinteger)
                    return mo_yr_post
                
                # if no change in year
                else:
                    mo_yr_post = calendar.month_abbr[monthinteger] + ' ' + str(today.strftime('%Y'))
                    return mo_yr_post

            # if no change in month
            else:
                mo_yr_post = str(today.strftime('%h')) + ' ' + str(today.strftime('%Y'))
                return mo_yr_post

        # if the number after the month is actually the day rather than the year
        elif int(mo_yr_post_group.group(2)) <= 31:
            today = datetime.now()
            mo_yr_post = mo_yr_post_group.group(1) + ' ' + str(today.strftime('%Y'))
            return mo_yr_post

        else:
            return mo_yr_post


    def start_requests(self):
                
        for start_url in self.start_urls:
            yield Request(url=start_url, callback=self.parse_attractions)


    def parse_attractions(self, response):

        # BOS' TripAdvisor page is set up differently than LAX, NYC, ORD
            # therefore, we need if statement to treat the xpath on the pages differently
        if response.url == self.start_urls[0]:
            
            # get the partial urls for the reviews of the top 5 attractions
                # once again, Boston's setup is different
                # we have to use a stepwise function to skip the urls ending in '#REVIEWS' so that we
                # do not have to account for those urls in parse_attractions_page's result_urls
            attrctn_to_rvw = response.xpath('//div[@class="_20eVZLwe"]/div/a/@href').extract()[0:9:2]
           
            # add the partial urls to the root url for the full url for each attraction review page
            review_page_1st_urls = [self.allowed_urls[0] + partial for partial in attrctn_to_rvw]
        
        else:
            
            # get the partial urls for the reviews of the top 10 attractions
            attrctn_to_rvw = response.xpath('//a[@class="_255i5rcQ"]/@href').extract()[:5]
                # results in:
                # ['/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html']
            
            # add the partial urls to the root url for the full url for each attraction review page
            review_page_1st_urls = [self.allowed_urls[0] + partial + '#REVIEWS' for partial in attrctn_to_rvw]
            # results in:
            # ['www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html']

        for rev_url in review_page_1st_urls:
            yield Request(url=rev_url, callback=self.parse_attractions_page)


    def parse_attractions_page(self, response):
        
        attraction = response.xpath('//h1[@class="ui_header h1"]/text()').extract_first()
        # results in:
        # 'The Getty Center'

        try:
            attraction_city = response.xpath('.//div[@class="_2kPIXVEi"]//a//text()').extract_first()
            attraction_city = ' '.join(attraction_city.split()[4:])
        except Exception as e:
            print(type(e), e)
            attraction_city = 0
        # 'Los Angeles'
        
        # get number of pages to create list of urls for each review page
        num_pages = int(response.xpath('//a[@class="pageNum "]/text()').extract()[-1])
        # each page (starting from 0) has a '-or#' sequence after "Reviews" where the multiple of 5
        # indicates the number of the last review of the previous page
            # therefore, '-or0' is pg 1, '-or5' is pg 2, '-or10' is page 3, etc

        if num_pages < 399:
            result_urls = [f'Reviews-or{(i+1)*5}-'.join(response.url.split('Reviews-')) for i in range(num_pages)]
        else:
            result_urls = [f'Reviews-or{(i+1)*5}-'.join(response.url.split('Reviews-')) for i in range(399)]
        
        result_urls.insert(0, response.url)
        # results in:
        # ['www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html#REVIEWS',
        # 'www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-or5-The_Getty_Center-Los_Angeles_California.html#REVIEWS',
        # 'www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-or10-The_Getty_Center-Los_Angeles_California.html#REVIEWS']

        meta = {'attraction_city': attraction_city,
                'attraction': attraction}

        for pg_url in result_urls:
            yield Request(url = pg_url, callback = self.parse_review_pages, meta=meta)


    def parse_review_pages(self, response):

        # gets the list of reviews using Scrapy
        reviews = response.xpath('.//div[@class="Dq9MAugU T870kzTX LnVzGwUB"]')
        
        # use Selenium to switch to active browser
        driver = webdriver.Chrome(r'C:\Users\tdcho\OneDrive\Desktop\NYCDSA\chromedriver.exe')
        driver.get(response.url)
        WebDriverWait(driver, 10)
        driver.maximize_window()
        # WebDriverWait(driver, 10)
        driver.switch_to.active_element
        # WebDriverWait(driver, 10)

        # gets the list of reviews using Selenium
        wait_review = WebDriverWait(driver, 10)
        selenium_reviews = wait_review.until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="Dq9MAugU T870kzTX LnVzGwUB"]')))

        # allows for concurrent scraping using Selenium and Scrapy
            # since selenium was used to grab review text after clicking 'read more',
            # review list using selenium was also used concurrently with scrapy list
        for selenium_review, review in zip(selenium_reviews, reviews):
            
            # gets the month and year that review was posted
            mo_yr_posted = review.xpath('.//div[@class="_2fxQ4TOx"]/span/text()').extract_first().split("review ")[1].strip()

            # convert 'yesterday' or 'month day' to 'month year'
            mo_yr_posted_final = self.get_mo_yr_posted(mo_yr_posted)
            
            # # Skips the review if the month and year posted is prior to Jan 2019
            # mo_yr_posted_obj = datetime.strptime(mo_yr_posted_final, '%b %Y')
            
            # # global posted_year 
            # posted_year = mo_yr_posted_obj.year
            
            # scrapy crawl tripadv_spider

            # if posted_year < 2019:
            #     break
            # else:
                
            # gets month and year visited if it exists
            try:
                mo_yr_visited = review.xpath('.//span[@class="_34Xs-BQm"]/text()').extract_first()
                mo_yr_visited = mo_yr_visited.strip()
            except Exception as e:
                print(type(e), e)
                mo_yr_visited = 0
               
            # use selenium to click on 1st 'read more' element as that expands all other review texts
            try:
                readmore = driver.find_element_by_xpath('//span[@class="_3maEfNCR"]')
                WebDriverWait(driver, 10)
                readmore.click()
                # Slows down the text expansion so the text can be scraped
                time.sleep(1)
            except:
                pass

            # get review text (there were some errors encountered during testing, so used 'try')
            try:
                rev_text = selenium_review.find_element_by_xpath('.//q[@class="IRsGHoPm"]').text
                rev_text = ' '.join(rev_text.split())
            except Exception as e:
                print(type(e), e)
                rev_text = 0

            # grabs username
            user = review.xpath('.//a[@class="ui_header_link _1r_My98y"]/text()').extract_first()

            # grabs user location if it exists
            try:
                user_loc = review.xpath('.//span[@class="default _3J15flPT small"]/text()').extract_first()
            except Exception as e:
                print(type(e), e)
                user_loc = 0

            # grabs the number of contributions (should be minimum of 1)
            num_contributions_user = review.xpath('.//span[@class="_1fk70GUn"]/text()').extract()[0]
            
            # gets the number of total helpful votes the user has accumulated
            try: 
                num_helpful_user = review.xpath('.//span[@class="_1fk70GUn"]/text()').extract()[1]
                num_helpful_user = int(re.findall('\d+', num_helpful_user)[0])
            except Exception as e:
                print(type(e), e)
                num_helpful_user = 0
                
            # get user rating
            rating = int(review.xpath('.//div[@data-test-target="review-rating"]//span/@class').extract_first().split(' bubble_')[1].strip('0') or '0')

            # get review title
            rev_title = review.xpath('.//div[@data-test-target="review-title"]//span/text()').extract_first()

            # gets number of helpful votes for that particular review
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
            item['mo_yr_posted_final'] = mo_yr_posted_final
            item['mo_yr_visited'] = mo_yr_visited
            item['num_helpful_votes'] = num_helpful_votes

            yield item

        driver.quit()

            


    