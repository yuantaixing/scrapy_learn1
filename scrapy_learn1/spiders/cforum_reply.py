# -*- coding: utf-8 -*-
import pymysql
import scrapy
import time

from scrapy_learn1.items import CforumReplyInfo


class CforumReplySpider(scrapy.Spider):
    name = "cforum_reply"

    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, db='stockinfo',
                                    user='root', passwd='')

        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')

    def start_requests(self):
        '''解析多个主题的回复,实现基于最新回帖日期的增量更新 '''

        print "==============start_requests=============="
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM `cforum_topicinfo` WHERE `new`='1'")
        dataset = cursor.fetchall()
        cursor.close()
        self.conn.commit()

        time = 0
        for data in dataset:
            # todo
            url = data[3]

            cursor = self.conn.cursor()
            cursor.execute("update cforum_topicinfo set new = %s where url = %s",
                           (False, url,))
            cursor.close()
            self.conn.commit()
            print "==============workonTopic=====================", time
            time += 1
            yield scrapy.Request(url=url, callback=self.parseReplyInfo, meta={"url": url})

            pass
        print "==============end_requests============="

        pass

    def parse(self, response):
        pass

    def parseReplyInfo(self, response):
        '''解析单个主题的回复 '''

        divs = response.xpath(".//div[@id='postlist']/div[contains(@id,'post_')]")
        for div in divs:
            # print "====len(divs)==========", len(divs)
            postnum = div.xpath(".//a[contains(@id,'postnum')]/em/text()").extract_first()
            # print "======postnum==========", postnum

            author = div.xpath(".//div[@class='authi']/a/text()").extract_first()
            # print "=====author======", author

            replytime = div.xpath(".//*[contains(@id,'authorposton')]/text()").extract_first().split("发表于")[1].strip()
            timeArray = time.strptime(replytime, "%d-%m-%Y %H:%M %p")
            replytime = time.strftime("%Y-%m-%d %H-%M ", timeArray)
            # print "=====replytime======", replytime

            quote_temp = div.xpath(".//td[contains(@id,'postmessage')]/div[@class='quote']")
            quote_info = div.xpath(
                ".//td[contains(@id,'postmessage')]/div[@class='quote']//a/font/text()").extract_first()
            if quote_info:
                # print "========quote_info==============", quote_info
                quote_author = quote_info.split("发表于")[0]
                quote_date = quote_info.split("发表于")[1].strip()
                timeArray = time.strptime(quote_date, "%d-%m-%Y %H:%M %p")
                quote_date = time.strftime("%Y-%m-%d %H-%M ", timeArray)

                # print "========quote_author==============", quote_author
                # print "========quote_date==============", quote_date

                quote = quote_temp.xpath("string()").extract_first().strip(quote_info)
                # print "========quote==============", quote
                content = div.xpath(".//td[contains(@id,'postmessage')]").xpath("string()").extract_first().strip(
                    quote_info + quote)
                # print "======content==========", content
                item = CforumReplyInfo(postnum=postnum, author=author, replytime=replytime,
                                       quote_author=quote_author, quote_date=quote_date, quote=quote, content=content,
                                       url=response.meta["url"])
            else:
                content = div.xpath(".//td[contains(@id,'postmessage')]").xpath("string()").extract_first()
                # print "======content==========", content
                item = CforumReplyInfo(postnum=postnum, author=author, replytime=replytime,
                                       quote_author='', quote_date='', quote='', content=content,
                                       url=response.meta['url'])
            print "\n\n"

            yield item
        pass
