# -*- coding:utf8 -*-
from __future__ import unicode_literals
import json
import datetime

from django.conf import settings
from horizon import redis
from django.utils.timezone import now

from users.models import User, Role


# 过期时间（单位：秒）
EXPIRES_24_HOURS = 24 * 60 * 60
EXPIRES_10_HOURS = 10 * 60 * 60


class UserCache(object):
    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_SETTINGS['host'],
                                    port=settings.REDIS_SETTINGS['port'],
                                    db=settings.REDIS_SETTINGS['db_set']['web'])
        self.handle = redis.Redis(connection_pool=pool)

    def get_user_id_key(self, user_id):
        return 'user_instance_id:%s' % user_id

    def get_user_name_key(self, user_name):
        return 'user_instance_phone:%s' % user_name

    def get_user_role_list_key(self):
        return 'user_role_list'

    def set_user_to_cache(self, key, data):
        self.handle.set(key, data)
        self.handle.expire(key, EXPIRES_24_HOURS)

    def get_user_by_id(self, request, user_id=None):
        if not request.user.is_admin:
            user_id = request.user.id
        key = self.get_user_id_key(user_id)
        user_instance = self.handle.get(key)
        if not user_instance:
            user_instance = User.get_object(**{'pk': user_id})
            if isinstance(user_instance, Exception):
                return user_instance
            self.set_user_to_cache(key, user_instance)
        return user_instance

    def get_user_by_username(self, user_name):
        key = self.get_user_name_key(user_name)
        user_instance = self.handle.get(key)
        if not user_instance:
            user_instance = User.get_object(**{'phone': user_name})
            if isinstance(user_instance, Exception):
                return user_instance
            self.set_user_to_cache(key, user_instance)
        return user_instance

    def get_user_role_list(self):
        key = self.get_user_role_list_key()
        list_data = self.handle.lrange(key)
        if not list_data:
            list_data = Role.filter_objects()
            if isinstance(list_data, Exception) or not list_data:
                return list_data
            self.handle.rpush(key, *list_data)
        return list_data

