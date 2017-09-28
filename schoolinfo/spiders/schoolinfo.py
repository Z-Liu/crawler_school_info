# encoding=utf-8
import re
from urlparse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class MySpider(CrawlSpider):
    name = 'myspider'
    allowed_domains = ['xuexiao.eol.cn']
    start_urls = ['http://xuexiao.eol.cn']
    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=('cengci=[小学|初中|高中]', 'html4/\d{4}/\d{9}/index.shtml$',), deny=('\?cengci=幼儿园',))),
        Rule(LinkExtractor(allow=('html4/\d{4}/\d{9}/intro.shtml$',)), callback='parse_item'),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        # Rule(LinkExtractor(allow=('intro\.shtml',)), callback='parse_item'),
    )

    def parse_item(self, response):
        self.logger.info('This is an item page! %s', response.url)

        class MyItem(scrapy.Item):
            province = scrapy.Field()
            city = scrapy.Field()
            name = scrapy.Field()
            introduction = scrapy.Field()
            administrative_code = scrapy.Field()
            stage = scrapy.Field()

        item = MyItem()
        province_city = response.xpath(
            "//table[@class='line_22']/tbody/tr[1]/td[2]/text()").extract()[0]
        re_match = re.match(ur"(.+省)(.+?市)", province_city)
        if re_match:
            item['province'] = re_match.group(1)
            item['city'] = re_match.group(2)
        else:
            item['province'] = ''
            re_match_city = re.match(ur"(.+?市)", province_city)
            item['city'] = re_match_city.group(1)
        # item['city'] = response.xpath('//table[@class="line_22"]/tbody/tr/td]').extract()[0].encode('utf-8')
        # l.add_xpath('name', '//h1/a[@href="index.html"]/text()')
        item['name'] = ''.join(response.xpath('//h1/a[@href="index.html"]/text()').extract()).strip().encode('utf-8')
        item['introduction'] = ''.join(response.xpath(
            "//div[@class='left_648 top_border']/div[@class='pad_20 line_22']/text()").extract()).strip().encode(
            'utf-8')
        # item['introduction'] = ''.join(response.xpath(
        #     '//div[@class="left_648 top_border"]/div[@class="pad_20 line_22"]/text()').extract()).strip().encode(
        #     'utf-8').replace('\r\n', '').replace('<p>', '').replace('<br>', '\r\n')
        item['administrative_code'] = urlparse(response.url).geturl().split('/')[4]
        item['stage'] = response.xpath(
            "//div[@class='left_648 img_border pad_top']/table[@class='line_22']/tbody/tr[3]/td[1]/font[@class='orange_12']/text()").extract()[
            0]
        return item
