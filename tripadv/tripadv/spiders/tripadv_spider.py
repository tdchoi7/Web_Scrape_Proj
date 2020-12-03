from tripadv.items import TripadvItem
from scrapy import Spider, Request
import re

class TripadvSpider(Spider):
	name = 'tripadv_spider'
	allowed_urls = ['https://www.tripadvisor.com']
	start_url_LAX = ['https://www.tripadvisor.com/Attractions-g32655-Activities-Los_Angeles_California.html']

	# may have to insert a click?

	LAX_url_1 = ['https://www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-The_Getty_Center-Los_Angeles_California.html#REVIEWS']

	# def parse_sort_by(self, response):
	# 	sort_by = response.xpath('//span[@class="_3GzCDlhA cDILN5_M"]/text()').extract


	def parse_landing_page(self, response):
		# get the partial urls for the reviews of the top 10 attractions
		attrctn_to_rvw = response.xpath('//a[@class="_3s_5RiH-"]/@href').extract()[:9]

		# apply the partial urls to the root url
		attrctn_rvw_urls = ['https://www.tripadvisor.com' + url for url in attrctn_to_rvw]

	def parse_results_page(self, response):
		num_pages = int(response.xpath('//a[@class="pageNum "]/text()').extract()[-1])

		# the webpage numbering seems to go by the number of the last review of the previous page starting with '-or0' and a 2nd page '-or5'
			# with 5 reviews per page, we would have to multiply the previous page number by 5 to get the correct webpage address
		page_urls_LAX_1 = [f'https://www.tripadvisor.com/Attraction_Review-g32655-d147966-Reviews-or{(i-1)*5}-The_Getty_Center-Los_Angeles_California.html' for i in range(num_pages)]

		date_posted_text = response.xpath('.//div[@class="_2fxQ4TOx"]/span/text()').extract()
		grouped = re.search('wrote a review (... \d+)', date_posted_text)
		dates_posted = grouped.group(0)

		for url in page_urls:
			# if page 
			yield Request(url=url, callback=self.parse_page_urls)

	def parse_reviews_page(self, response):
		review_page