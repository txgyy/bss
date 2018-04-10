#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor, defer,task
from scrapy.crawler import CrawlerRunner,CrawlerProcess
from scrapy.utils.project import get_project_settings
from itertools import product
from scrapy.utils.log import configure_logging
from bss.spiders.bss0 import Bss0Spider
from redis import StrictRedis
from datetime import datetime
from time import sleep
configure_logging()
runner = CrawlerProcess(get_project_settings())
redis = StrictRedis.from_url(get_project_settings().get('REDIS_URL'))
@defer.inlineCallbacks
def crawl():
    # yield redis.delete('dupefilter:timestamp')
    print(datetime.now().time(),': start')
    yield runner.crawl(Bss0Spider,'dongweiming',True)
    yield runner.crawl(Bss0Spider,'dongweiming',False)
    print(datetime.now().time(),': finish')
    reactor.stop()


if __name__ == '__main__':
    # task.LoopingCall(crawl).start(600)
    # task.LoopingCall(crawl,False).start(60*60*24)
    crawl()
    reactor.run()
