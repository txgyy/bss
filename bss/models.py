#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import CHAR,Integer,Enum,Boolean
from sqlalchemy.dialects.mysql import TINYINT,MEDIUMINT
from sqlalchemy import Column,PrimaryKeyConstraint,Index,UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine,MetaData,Table
from sqlalchemy.orm import sessionmaker
from scrapy.utils.project import get_project_settings

Base = declarative_base()

class userModel(Base):
    __tablename__ = 'user'
    auto_id = Column(Integer,primary_key=True,autoincrement=True)
    url_token = Column(CHAR(length=70),unique=True)
    name = Column(CHAR(length=40))
    gender = Column(TINYINT)
    headline = Column(CHAR(length=160))
    follower_count = Column(MEDIUMINT)
    answer_count = Column(MEDIUMINT)
    articles_count = Column(MEDIUMINT)
    user_type = Column(Enum('people','organization','guest'),default='people')
    id = Column(CHAR(32))
    is_advertiser = Column(Boolean)
    is_org = Column(Boolean)

class guanxiModel(Base):
    __tablename__ = 'guanxi'
    __table_args__ = (
        UniqueConstraint('s_url_token', 'url_token', name='guanxi_uk'),
    )
    auto_id = Column(Integer,primary_key=True,autoincrement=True)
    s_url_token = Column(CHAR(length=70))
    followee_count = Column(MEDIUMINT)
    url_token = Column(CHAR(length=70))

zhihu_engine = create_engine(
    get_project_settings().get('MYSQL_URL').format(db='zhihu'),
    # echo=True
)
zhihu_metadata = MetaData(zhihu_engine)

urlsTable = Table(
    'urls',zhihu_metadata,
    Column('status',Enum('fail', 'success', 'deny')),
    Column('url_token',CHAR(length=70)),
    Column('offset',MEDIUMINT),
    PrimaryKeyConstraint('status','url_token','offset',name='urls_pk')
)
userTable = userModel.__table__
guanxiTable = guanxiModel.__table__
userTable.metadata = zhihu_metadata
guanxiTable.metadata = zhihu_metadata

zhihu_metadata.create_all(tables=[userTable,guanxiTable, urlsTable])
ZhihuSession = sessionmaker(bind=zhihu_engine,autocommit=True)

ipproxy_engine = create_engine(
    get_project_settings().get('MYSQL_URL').format(db='ipproxy'),
    # echo=True
)
ipproxy_metadata = MetaData(ipproxy_engine)
IpproxySession = sessionmaker(bind=ipproxy_engine,autocommit=True)

