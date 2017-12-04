# -*- coding:utf8 -*-
from __future__ import unicode_literals
import json
import datetime

from django.conf import settings
from horizon import redis
from django.utils.timezone import now

from reports.models import (Report,
                            ReportDownloadRecord)

# 过期时间（单位：秒）
EXPIRES_24_HOURS = 24 * 60 * 60
EXPIRES_10_HOURS = 10 * 60 * 60


class ReportCache(object):
    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_SETTINGS['host'],
                                    port=settings.REDIS_SETTINGS['port'],
                                    db=settings.REDIS_SETTINGS['db_set']['web'])
        self.handle = redis.Redis(connection_pool=pool)

    def get_report_id_key(self, pk):
        return 'report:id:%s' % pk

    def get_report_download_record_list_id_key(self, user_id):
        return 'report_download_record:user_id:%s' % user_id

    def set_instance_to_cache(self, key, data):
        self.handle.set(key, data)
        self.handle.expire(key, EXPIRES_24_HOURS)

    def get_instance_from_cache(self, key):
        return self.handle.get(key)

    def get_perfect_data(self, key, model_function, **kwargs):
        data = self.get_instance_from_cache(key)
        if not data:
            data = model_function(**kwargs)
            if isinstance(data, Exception):
                return data
            self.set_instance_to_cache(key, data)
        return data

    # 获取报告文件下载记录列表
    def get_report_download_record_by_user_id(self, user_id):
        key = self.get_report_download_record_list_id_key(user_id)
        list_data = self.handle.lrange(key)
        if not list_data:
            list_data = ReportDownloadRecord.filter_details(**{'user_id': user_id})
            if isinstance(list_data, Exception):
                return list_data
            self.handle.rpush(key, *list_data)
        return list_data

    # 往报告文件下载列表里添加数据
    def insert_data_to_report_download_record(self, user_id, detail):
        key = self.get_report_download_record_list_id_key(user_id)
        return self.handle.rpushx(key, detail)

