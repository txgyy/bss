# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy_sqlalchemyitem import SqlalchemyItem
from .models import userModel,guanxiModel

class userItem(SqlalchemyItem):
    sqlalchemy_model = userModel

class guanxiItem(SqlalchemyItem):
    sqlalchemy_model = guanxiModel

