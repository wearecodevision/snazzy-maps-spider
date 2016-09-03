# -*- coding : urf-8 -*-

import scrapy
import math


class SnazzyMapsSpider(scrapy.Spider):
	name = "Snazzy Maps"	
	index = 0
	count = 0
	per_page = 12
	base_url = "https://snazzymaps.com"
	page_argument = "page"

	def __init__(self, *args, **kwargs):
		if 'sort' in kwargs and kwargs['sort'] == "popular":
			self.start_urls = ["https://snazzymaps.com/explore?sort=popular"]
		else:
			self.start_urls = ["https://snazzymaps.com/explore?"]		

		if 'count' in kwargs:
			self.count = int(kwargs['count'])

	def parse(self, response):		
		if self.count is not 0:
			num_pages = int(math.ceil(float(self.count) / float(self.per_page)))
		else:
			pages_list = response.css('.pagination li')
			num_pages = int(pages_list[-2].css('a::text').extract()[0])
		

		for i in range(1, num_pages + 1):
			yield scrapy.Request("{0}&{1}={2}".format(self.start_urls[0], self.page_argument, i), self.parse_page)

	def parse_page(self, response):
		items = response.css('.explore-list .container-preview')

		for item in items:
			if self.count is 0 or self.count > self.index:
				self.index += 1								
				link = item.css('.preview-details.btn-no-underline::attr("href")').extract()[0]							
				yield scrapy.Request("{0}{1}".format(self.base_url, link), self.parse_item)


	def parse_item(self, response):
		styles = response.css('#style-json::text').extract()[0].strip().replace('\r', '').replace('\n', '')
		styles = ' '.join(styles.split())

		stats = response.css('.stats div')
		stats = int(stats[0].css('span::text').extract()[0].split()[0])

		yield { 
			'name': response.css('h1.media span.name::text').extract()[0],
			'url': response.url,
			'styles': styles,
			'views': stats,
		}			