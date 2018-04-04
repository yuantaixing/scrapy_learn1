#!/usr/bin/python
# -*- coding: utf-8 -*-
import pymysql
import requests


class ProxyHelper:
    '''检测爬虫爬取的ip的有效性'''

    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, db='stockinfo',
                                    user='root', passwd='')
        pass

    def visiteNet(self, ip):
        proxies = {"http": ip, }
        # url = 'https://www.baidu.com/'
        # url = 'http://tool.chinaz.com/ipwhois'
        url = 'http://www.gsmarena.com/makers.php3'
        try:
            response = requests.get(url, proxies=proxies)
            print "========response.headers:=========", response.headers
            # print " ==========response.text:==========", response.text
            return True
        except Exception, e:
            print "======the error is=======", e
            return False
            pass

    def getIpsFromSql(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM `ips` ")
        dataset = cursor.fetchall()
        cursor.close()
        self.conn.commit()
        return dataset

    def checkIp(self):
        dataset = self.getIpsFromSql()
        last_num = len(dataset)
        print "current ips is:", last_num
        print "now is checking..."

        time = 0
        for data in dataset:
            ip = data[0] + ":" + str(data[1])
            if not self.visiteNet(ip):
                self.removeIpFromSql(ip)
                last_num = last_num - 1
                print "current ips is:", last_num
            time += 1
            print "now is checking...", time

        dataset = self.getIpsFromSql()
        print "the checking is over"
        print "the ips finally can be used is :", len(dataset)

    def checkIps(self, ips):
        '''检测一组ip'''
        ips_temp = ips[:]
        for ip in ips:
            if not self.visiteNet(ip):
                ips_temp.remove(ip)
        pass
        return ips_temp

    def removeIpFromSql(self, ip):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM `ips` WHERE ip=%s", ip.split(":")[0])
        cursor.close()
        self.conn.commit()
        pass

    def getipFromTxt(self):
        return [line.split(",")[0] for line in open("ips.txt", "r") if not line.split(",")[2].startswith("中国")]

    def saveIps_txt(self, ips):
        with open("ips_pure.txt", "a") as f:
            for ip in ips:
                f.write('"' + str(ip) + '"' + ",")

    pass


if __name__ == '__main__':
    proxyHelper = ProxyHelper()
    # proxyHelper.checkIp()
    # proxyHelper.visiteNet("101.247.67.9:53281")
    # proxyHelper.removeIpFromSql("101.247.67.9:53281")
    ips = ["104.236.111.156:8118", "177.113.0.115:8080", "59.152.94.254:8080",
           "159.203.48.136:80", "184.82.128.210:8080", "41.185.29.40:3128", "178.49.11.160:53281",
           "152.251.78.184:8080"]
    # ips = proxyHelper.getipFromTxt()
    ips = proxyHelper.checkIps(ips)
    print ips
    proxyHelper.saveIps_txt(ips)
