# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy import signals
from fake_useragent import UserAgent
import random
from scrapy.spidermiddlewares.httperror import HttpError, IgnoreRequest
import re
import json
import brotli
from .models import urlsTable, ZhihuSession, IpproxySession, ipproxy_metadata
from sqlalchemy import Table


class ZhihuSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        self.zhihu_session = ZhihuSession()

    def spider_closed(self, spider):
        self.zhihu_session.close()

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.
        # Should return None or raise an exception.
        if 200 <= response.status <= 300:
            if response.headers.get('Content-Encoding') == 'br':
                response.meta['content'] = json.loads(brotli.decompress(response.body))
            else:
                response.meta['content'] = json.loads(response.body_as_unicode())
        else:
            raise HttpError

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.
        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def update_url(self, spider, http, status='success'):
        return update_url(self, spider, http, status)


class ZhihuDownloaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        o = cls()
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.httpbinTable = Table('httpbin', ipproxy_metadata)
        self.ipproxy_session = IpproxySession()
        self.zhihu_session = ZhihuSession()

        self.err_proxy = set()
        self.proxy = set()
        self.useragent = UserAgent()

        self.ok_url = set(self.get_status_urls(spider, 'success'))

    def spider_closed(self, spider):
        self.ipproxy_session.close()
        self.zhihu_session.close()

    def process_request(self, request, spider):
        headers = {
            'User-Agent': self.useragent.random
        }
        for k, v in headers.items():
            request.headers[k] = v

    def process_response(self, request, response, spider):
        return response

    # def process_exception(self, request, exception, spider):
    #     pass

    def change_proxy(self, request, spider):
        if self.proxy == self.err_proxy:
            self.err_proxy = set()
            # 两种查询方式
            self.proxy = self.ipproxy_session.query(self.httpbinTable.ip, self.httpbinTable.port).all()
            # self.HttpbinTable.select().with_only_columns([self.HttpbinTable.ip,self.HttpbinTable.port]).execute().fetchall()
        request.meta['proxy'] = 'https://{}:{}'.format(*random.choice(list(self.proxy - self.err_proxy)))

    def update_url(self, spider, request, status='success'):
        return update_url(self, spider, request, status)

    def get_status_urls(self, spider, status):
        # 两种选择方法
        r = self.zhihu_session.query(urlsTable.c.url_token, urlsTable.c.offset).filter(urlsTable.c.status == status).all()
        # r = UrlsTable.select(UrlsTable.c.status==status).with_only_columns([UrlsTable.c.url_token,UrlsTable.c.offset]).execute().fetchall()
        return set(r)


def update_url(self, spider, request, status='success'):
    pattern = re.compile(r'members/(.*?)/followees.*?offset=(\d+)&limit=20')
    url_token, offset = pattern.search(request.url).groups()
    try:
        if status == 'success':
            # 两种删除方法
            self.zhihu_session.query(urlsTable).filter_by(status='fail', url_token=url_token, offset=offset).delete()
            # UrlsTable.delete(UrlsTable.c.status == 'fail' and UrlsTable.c.url_token == url_token and UrlsTable.c.offset == offset).execute()
        if not request.meta.get('url_retry') or status == 'success':
            # 两种插入方法
            self.zhihu_session.add(urlsTable(status=status, url_token=url_token, offset=offset))
            # UrlsTable.insert().values(status=status,url_token=url_token,offset=offset).execute()
    except Exception as e:
        self.zhihu_session.rollback()
        spider.logger.error(e)
