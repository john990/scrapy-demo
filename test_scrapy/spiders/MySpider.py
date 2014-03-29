import sys
import os

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from selenium import selenium

from test_scrapy.items import TestScrapyItem


class MySpider(CrawlSpider):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    path = 'article/'
    if not os.path.exists(path):
        os.makedirs(path)

    name = "spider"
    allowed_domains = ["yue.fm"]
    start_urls = [
        "http://yue.fm/bcd6v"
    ]

    rules = [
        Rule(SgmlLinkExtractor(allow=('/[^/]+$')), callback="parse")
    ]

    def __init__(self):
        CrawlSpider.__init__(self)
        self.verification_errors = []
        self.selenium = selenium("localhost", 4444, "*firefox",  "http://yue.fm/")
        self.selenium.start()

    def __del__(self):
        self.selenium.stop()
        print self.verification_errors
        CrawlSpider.__del__(self)

    def parse(self, response):
        print 'loading url:' + response.url

        s = self.selenium
        s.open(response.url)
        s.wait_for_page_to_load("30000")
        import time

        time.sleep(2.5)

        title = s.xpath("//div[@class='article']/h1[@class='title'][1]/text()").extract()[0]
        author = s.xpath("//div[@class='article']/div[@class='body']/p[1]/b/text()").extract()[0]
        content = s.xpath("//div[@class='article']/div[@class='body']/p[position()>1]").extract()

        self.write_content(title, content)

        next_url = s.xpath("//div[@class='next']/a[@id='next']/@href").extract()
        print next_url
        yield Request(next_url)

        item = TestScrapyItem()
        item['title'] = title
        item['link'] = response.url
        item['author'] = author
        item['content'] = content

        yield item


    def write_content(self, title, content):
        filename = self.path + title
        # print filename
        f = file(filename, 'w')
        for p in content:
            f.write(p)