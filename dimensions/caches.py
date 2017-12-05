# -*- coding:utf8 -*-
from __future__ import unicode_literals
import json
import datetime

from django.conf import settings
from horizon import redis
from django.utils.timezone import now

from dimensions.models import (Dimension,
                               Attribute,
                               Tag,
                               TagConfigure,
                               AdjustCoefficient)

# 过期时间（单位：秒）
EXPIRES_24_HOURS = 24 * 60 * 60
EXPIRES_10_HOURS = 10 * 60 * 60


class DimensionCache(object):
    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_SETTINGS['host'],
                                    port=settings.REDIS_SETTINGS['port'],
                                    db=settings.REDIS_SETTINGS['db_set']['web'])
        self.handle = redis.Redis(connection_pool=pool)

    def get_dimension_id_key(self, dimension_id):
        return 'dimension:id:%s' % dimension_id

    def get_dimension_list_key(self):
        return 'dimension_list'

    def get_attribute_id_key(self, attribute_id):
        return 'attribute:id:%s' % attribute_id

    def get_attribute_list(self):
        return 'attribute_list'

    def get_tag_id_key(self, tag_id):
        return 'tag:id:%s' % tag_id

    def get_tag_list_key(self, dimension_id):
        return 'tag_list:dimension_id:%s' % dimension_id

    def get_adjust_coefficient_name_key(self, name):
        return 'adjust_coefficient:name:%s' % name

    def set_instance_to_cache(self, key, data):
        self.handle.set(key, data)
        self.handle.expire(key, EXPIRES_24_HOURS)

    def get_instance_from_cache(self, key):
        return self.handle.get(key)

    def set_list_to_cache(self, key, *list_data):
        self.handle.rpush(key, *list_data)
        self.handle.expire(key, EXPIRES_24_HOURS)

    def get_list_from_cache(self, key, start=0, end=-1):
        return self.handle.lrange(key, start, end)

    def get_perfect_data(self, key, model_function, **kwargs):
        data = self.get_instance_from_cache(key)
        if not data:
            data = model_function(**kwargs)
            if isinstance(data, Exception):
                return data
            self.set_instance_to_cache(key, data)
        return data

    def get_perfect_list_data(self, key, model_function, **kwargs):
        list_data = self.get_list_from_cache(key)
        if not list_data:
            list_data = model_function(**kwargs)
            if isinstance(list_data, Exception):
                return list_data
            self.set_list_to_cache(key, list_data)
        return list_data

    # 获取维度Model Instance
    def get_dimension_by_id(self, dimension_id):
        key = self.get_dimension_id_key(dimension_id)
        kwargs = {'pk': dimension_id}
        return self.get_perfect_data(key, Dimension.get_object, **kwargs)

    # 获取属性Model instance
    def get_attribute_by_id(self, attribute_id):
        key = self.get_attribute_id_key(attribute_id)
        kwargs = {'pk': attribute_id}
        return self.get_perfect_data(key, Attribute.get_object, **kwargs)

    # 获取标签Model instance
    def get_tag_by_id(self, tag_id):
        key = self.get_tag_id_key(tag_id)
        kwargs = {'pk': tag_id}
        return self.get_perfect_data(key, Tag.get_object, **kwargs)

    # 获取维度List
    def get_dimension_list(self):
        key = self.get_dimension_list_key()
        return self.get_perfect_list_data(key, Dimension.filter_objects, **{})

    # 获取标签List
    def get_tag_list_by_dimension_id(self, dimension_id):
        key = self.get_tag_list_key(dimension_id)
        kwargs = {'dimension_id': dimension_id}
        return self.get_perfect_list_data(key, Tag.filter_objects_by_dimension_id, **kwargs)

    # 获取调整系数Model instance
    def get_adjust_coefficient_by_name(self, adjust_coefficient_name):
        key = self.get_adjust_coefficient_name_key(adjust_coefficient_name)
        kwargs = {'name': adjust_coefficient_name}
        return self.get_perfect_data(key, AdjustCoefficient.get_object, **kwargs)


