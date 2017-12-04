# -*- coding:utf8 -*-
from __future__ import unicode_literals
import json
import datetime

from django.conf import settings
from horizon import redis
from django.utils.timezone import now

from score.models import (Score,
                          ScoreRecord,
                          SCORE_ACTION_DICT)

# 过期时间（单位：秒）
EXPIRES_24_HOURS = 24 * 60 * 60
EXPIRES_10_HOURS = 10 * 60 * 60


class ScoreCache(object):
    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_SETTINGS['host'],
                                    port=settings.REDIS_SETTINGS['port'],
                                    db=settings.REDIS_SETTINGS['db_set']['web'])
        self.handle = redis.Redis(connection_pool=pool)

    def get_score_id_key(self, user_id):
        return 'score_id:%s' % user_id

    def get_score_record_id_key(self, user_id):
        return 'score_record:%s' % user_id

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

    # 获取score model
    def get_score_instance_by_user_id(self, user_id):
        key = self.get_score_id_key(user_id)
        data = self.get_instance_from_cache(key)
        if not data:
            data = Score.get_object(user_id=user_id)
            if isinstance(data, Exception):
                init_dict = {'user_id': user_id,
                             'score': 0,
                             'created': now(),
                             'updated': now()}
                data = Score(**init_dict)
            self.set_instance_to_cache(key, data)
        return data

    # 删除score model
    def delete_score_instance_by_user_id(self, user_id):
        key = self.get_score_id_key(user_id)
        return self.handle.delete(key)

    # 获取积分记录列表
    def get_score_record_by_user_id(self, user_id):
        key = self.get_score_record_id_key(user_id)
        list_data = self.handle.lrange(key)
        if not list_data:
            list_data = ScoreRecord.filter_objects(**{'user_id': user_id})
            if isinstance(list_data, Exception):
                return list_data
            self.handle.rpush(key, *list_data)
        return list_data

    # 往积分记录列表里添加数据
    def insert_score_instance_to_score_record(self, user_id, instance):
        key = self.get_score_record_id_key(user_id)
        data = self.get_score_record_by_user_id(user_id)
        if isinstance(data, Exception):
            return data
        else:
            self.handle.rpush(key, instance)
        return True


class ScoreAction(object):
    """
    积分操作
       : 增加或减少积分，并添加积分记录
    """
    @classmethod
    def update_score(cls, request, action='comment'):
        # 更新缓存
        ScoreCache().delete_score_instance_by_user_id(request.user.id)
        return Score.update_score(request, action=action)

    @classmethod
    def create_score_record(cls, request, action='comment'):
        if action not in SCORE_ACTION_DICT:
            return Exception('Params [action] is incorrect.')

        init_data = {'user_id': request.user.id,
                     'action': SCORE_ACTION_DICT[action]['action'],
                     'score_count': SCORE_ACTION_DICT[action]['score']}
        record = ScoreRecord(**init_data)
        record.save()
        # 更新缓存
        ScoreCache().insert_score_instance_to_score_record(request.user.id, record)
        return record

    @classmethod
    def score_action(cls, request, action='comment'):
        score = cls.update_score(request, action=action)
        if isinstance(score, Exception):
            return score
        record = cls.create_score_record(request, action=action)
        if isinstance(record, Exception):
            return record
        return score, record

