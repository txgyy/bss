# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from .items import userItem, guanxiItem
from .models import userModel, guanxiModel, ZhihuSession
from scrapy_redis.pipelines import RedisPipeline
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import Insert

class ZhihuPipeline(object):
    def open_spider(self, spider):
        self.session = ZhihuSession()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        model = globals().get(item.__class__.__name__[:-4] + 'Model')
        try:
            self.insert(model, item)
        except Exception as e:
            self.session.rollback()
            spider.logger(e)
        return item

    def update(self, model, item):
        self.session.bulk_update_mappings(model, map(lambda v: dict(zip(item.keys(), v)), zip(*item.values(), )))

    def insert(self, model, item):
        self.session.bulk_insert_mappings(model, map(lambda v: dict(zip(item.keys(), v)), zip(*item.values(), )))


class FolloweesRedisPipeline(RedisPipeline):
    def _process_item(self, item, spider):
        key = self.item_key(item, spider)
        data = map(lambda v: self.serialize(dict(zip(item.keys(), v))), zip(*item.values(), ))
        self.server.rpush(key, *data)
        return item

    def item_key(self, item, spider):
        return self.key % {'item': item.__class__.__name__}

@compiles(Insert)
def insert_ignore(insert, compiler, **kw):
    s = compiler.visit_insert(insert, **kw)
    s = s.replace("INSERT", "INSERT IGNORE")
    return s