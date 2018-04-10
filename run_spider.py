#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from bss.spiders.bss0 import Bss0Spider

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(Bss0Spider,'dongweiming',True)
    process.start()
