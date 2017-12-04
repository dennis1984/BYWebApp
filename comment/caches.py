# -*- coding:utf8 -*-
from __future__ import unicode_literals
import json
import datetime

from django.conf import settings
from horizon import redis
from django.utils.timezone import now

from comment.models import (Comment,
                            ReplyComment,
                            CommentOpinionRecord)

# 过期时间（单位：秒）
EXPIRES_24_HOURS = 24 * 60 * 60
EXPIRES_10_HOURS = 10 * 60 * 60


class CommentCache(object):
    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_SETTINGS['host'],
                                    port=settings.REDIS_SETTINGS['port'],
                                    db=settings.REDIS_SETTINGS['db_set']['web'])
        self.handle = redis.Redis(connection_pool=pool)

    def get_comment_list_user_id_key(self, user_id):
        return 'comment:list:user_id:%s' % user_id

    def get_comment_list_source_id_key(self, source_type, source_id):
        return 'comment:list:source_id:%s-%s' % (source_type, source_id)

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

    # 获取用户评论列表
    def get_comment_list_by_user_id(self, user_id):
        key = self.get_comment_list_user_id_key(user_id)
        kwargs = {'user_id': user_id}
        return self.get_perfect_list_data(key, Comment.filter_details, **kwargs)

    # 获取资源的评论列表
    def get_comment_list_by_source_id(self, source_type, source_id):
        key = self.get_comment_list_source_id_key(source_type, source_id)
        kwargs = {'source_type': source_type,
                  'source_id': source_id}
        return self.get_perfect_list_data(key, Comment.filter_details, **kwargs)


class CommentOpinionModelAction(object):
    """
    对评论的评价（点赞/踩）操作
    """
    @classmethod
    def update_comment_opinion_count(cls, comment_id, action=1):
        return Comment.update_opinion_count(comment_id, action=action)

    @classmethod
    def create_comment_opinion_record(cls, request, comment_id, action=1):
        init_data = {'user_id': request.user.id,
                     'comment_id': comment_id,
                     'action': action}
        record = CommentOpinionRecord(**init_data)
        try:
            record.save()
        except Exception as e:
            return e
        return record

    @classmethod
    def comment_opinion_action(cls, request, comment_id, action=1):
        comment = cls.update_comment_opinion_count(comment_id, action)
        if isinstance(comment, Exception):
            return comment
        record = cls.create_comment_opinion_record(request, comment_id, action=action)
        if isinstance(record, Exception):
            return record
        return comment, record
