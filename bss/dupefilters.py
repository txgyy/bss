#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy_redis.dupefilter import RFPDupeFilter
from scrapy_redis.connection import get_redis_from_settings
import hashlib
import weakref
from scrapy.utils.python import to_bytes

from w3lib.url import canonicalize_url

_fingerprint_cache = weakref.WeakKeyDictionary()
class ZhihuRFPDupeFilter(RFPDupeFilter):
    @classmethod
    def from_settings(cls, settings):
        server = get_redis_from_settings(settings)
        key = settings.get('DUPEFILTER_KEY')
        debug = settings.getbool('DUPEFILTER_DEBUG')
        return cls(server, key=key, debug=debug)

    def request_fingerprint(self, request):
        cache = _fingerprint_cache.setdefault(request, {})
        if None not in cache:
            fp = hashlib.sha1()
            fp.update(to_bytes(canonicalize_url(request.url)))

            cache[None] = request.url
        return cache[None]
    def close(self, reason=''):
        pass