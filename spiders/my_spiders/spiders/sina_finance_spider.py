#!/usr/bin/env python
# coding=utf-8
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor

from scrapy.http import Request
from my_spiders.items import NewsItem
import re
import json


class SinaFinanceSpider(Spider):
    name = "sina_news_spider"  # name of spiders
    start_urls = ["http://interface.sina.cn/wap_api/layout_col.d.json?show_num=40&page=1&act=more"]
    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,  # 设置请求延迟
    }

    def parse(self, response):  # rules得到的转移到这里，在Rule里面没有callback="parse",follow=True
        data = json.loads(response.body_as_unicode())
        cur_page = int(re.findall(u'page=(\d+)', response.url))
        if "result" in data:
            if data["result"]["status"]["code"] = 0:
                news = data["result"]["data"]
                total = news["total"]
                count = news["count"]
                for newItem in news["list"]:
                    self.parse_content(newItem)

                yield scrapy.Request(url = "http://interface.sina.cn/wap_api/layout_col.d.json?show_num=40&page=%d&act=more" % cur_page + 1, callback=self.parse)

    def parse_content(self, newItem):
        item = NewsItem()
        item["newsId"] = newItem["_id"]
        item['url'] = newItem["URL"]
        item['title'] = newItem["title"]
        item['s_title'] = newItem["s_title"]
        item['date'] = newItem["cdateTime"]
        item["source"] = newItem["source"]
        item["summary"] = newItem["summary"]
        pics = []
        for pic in newItem["allPics"]["pics"]:
            pic.append(pic)
        item["pics"] = ",".join(pics)
        
        yield item

    def getArticl(self, newItem):
        url = newItem["URL"]
        artical_resp = requests.get(url)
        if "games.sina" in url:
            item["content"] = "\n".join(artical_resp.xpath("//div[@class='articleContent']//p/text()").extract())
            item["category"] = "games"
        elif "blog.sina" in url:
            item["category"] = "blog"
            item["content"] = "\n".join(artical_resp.xpath("//div[contains(@class, 'content')]/text()").extract())
            item["author"] = artical_resp.xpath("//span[@data-role='title']/text()").extract_first()
        elif "k.sina" in url:
            item["category"] = re.findall(u'from=(\w+)', url) + "," + re.findall(u'subch=(\w+)', url)
            item["content"] = "\n".join(artical_resp.xpath("//section[contains(@class,'art_content')]//p//text()").extract())
        elif "yd.sina" in url:
            item["category"] = 
            item["content"] = "\n".join(artical_resp.xpath("//div[@class='art_t']/text()").extract())
        else:
            item["category"] = ",".join(artical_resp.xpath("//ul[@class='h_nav_items']//a/@title").extract())
            item["content"] = "\n".join(artical_resp.xpath("//p[@class='art_t']/text()").extract())



