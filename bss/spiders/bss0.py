# -*- coding: utf-8 -*-
import scrapy
from bss.items import userItem, guanxiItem
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from bss.models import guanxiTable


class Bss0Spider(scrapy.Spider):
    name = 'bss0'
    allowed_domains = ['www.zhihu.com']
    custom_settings = {
        # 'LOG_FILE': 'logs/followees.log',
        # 'JOBDIR': 'crawls/followees'
        'ITEM_PIPELINES': {
            # 'bss.pipelines.FolloweesRedisPipeline': 300,
            'bss.pipelines.ZhihuPipeline': 300,
        },
    }

    def __init__(self, url_token, first, **kwargs):
        super(Bss0Spider, self).__init__(**kwargs)
        self.url_token = url_token
        self.first = first
        self.base_url = 'https://www.zhihu.com/api/v4/members/{url_token:s}/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count&offset={offset:d}&limit=20'

    def start_requests(self):
        if self.first:
            yield scrapy.Request(
                url=self.base_url.format(url_token=self.url_token, offset=0),
                meta={
                    's_url_token': self.url_token,
                    'offset': 0,
                },
            )
        else:
            url_tokens = guanxiTable.select(guanxiTable.c.s_url_token == self.url_token).with_only_columns(
                [guanxiTable.c.url_token]).execute().fetchall()
            for url_token, in url_tokens:
                yield scrapy.Request(
                    url=self.base_url.format(url_token=url_token, offset=0),
                    meta={
                        's_url_token': url_token,
                        'offset': 0,
                    },
                )

    def parse(self, response):
        guanxi = ItemLoader(item=guanxiItem())
        user = ItemLoader(item=userItem())
        contents = response.meta.get('content')

        followee_count = contents['paging']['totals']
        s_url_token = response.meta['s_url_token']
        for followee in contents['data']:
            url_token = followee.get('url_token')
            guanxi.add_value('s_url_token', s_url_token)
            guanxi.add_value('followee_count', followee_count)
            guanxi.add_value('url_token', url_token)

            for key in userItem.fields.keys():
                if key == 'headline':
                    followee['headline'] = Selector(text=followee.get(key)).xpath('string(.)').extract_first() or ''
                user.add_value(key, followee.get(key))

        yield guanxi.load_item()
        yield user.load_item()
        # 只有第一个请求才会通过
        if followee_count > 20 and response.meta.get('offset') == 0:
            for offset in range(20, followee_count, 20):
                url = self.base_url.format(url_token=s_url_token, offset=offset)
                yield scrapy.Request(
                    url=url,
                    meta={
                        's_url_token': s_url_token,
                        'offset': offset,
                    },
                )
