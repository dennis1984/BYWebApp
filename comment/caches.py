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

    def get_comment_detail_id_key(self, comment_id):
        return 'comment_detail:comment_id:%s' % comment_id

    def set_instance_to_cache(self, key, data):
        self.handle.set(key, data)
        self.handle.expire(key, EXPIRES_24_HOURS)

    def get_instance_from_cache(self, key):
        return self.handle.get(key)

    def set_list_to_cache(self, key, *list_data):
        self.handle.delete(key)
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

            # 把每条评论逐次添加都缓存中
            for item_data in list_data:
                detail_key = self.get_comment_detail_id_key(item_data['id'])
                if not self.get_instance_from_cache(detail_key):
                    self.set_instance_to_cache(detail_key, item_data)
            # 生成评论列表
            perfect_list_data = [item['id'] for item in list_data]
            self.set_list_to_cache(key, *perfect_list_data)
            return list_data
        return list_data

    # 获取用户评论列表
    def get_comment_list_by_user_id(self, user_id):
        key = self.get_comment_list_user_id_key(user_id)
        kwargs = {'user_id': user_id}
        ids_list = self.get_perfect_list_data(key, Comment.filter_details, **kwargs)
        return self.get_perfect_list_data_by_ids(ids_list)

    # 获取资源的评论列表
    def get_comment_list_by_source_id(self, source_type, source_id):
        key = self.get_comment_list_source_id_key(source_type, source_id)
        kwargs = {'source_type': source_type,
                  'source_id': source_id}
        ids_list = self.get_perfect_list_data(key, Comment.filter_details, **kwargs)
        return self.get_perfect_list_data_by_ids(ids_list)

    def get_perfect_list_data_by_ids(self, ids_list):
        perfect_list_data = []
        for comment_id in ids_list:
            id_key = self.get_comment_detail_id_key(comment_id)
            kwargs = {'id': comment_id}
            detail = self.get_perfect_data(id_key, Comment.get_detail, **kwargs)
            if isinstance(detail, Exception):
                continue
            perfect_list_data.append(detail)
        return perfect_list_data

    # 从用户评论列表中删除评论数据
    def delete_comment_from_user_comment_list(self, user_id, comment_id):
        key = self.get_comment_list_user_id_key(user_id)
        return self.delete_from_cache_list_action(key, comment_id)

    # 从资源评论列表中删除评论数据
    def delete_comment_form_source_comment_list(self, source_type, source_id, comment_id):
        key = self.get_comment_list_source_id_key(source_type, source_id)
        return self.delete_from_cache_list_action(key, comment_id)

    def delete_from_cache_list_action(self, key, comment_id):
        ids_list = self.get_list_from_cache(key)
        if comment_id in ids_list:
            ids_list.remove(comment_id)
            self.set_list_to_cache(key, ids_list)
            return 1
        return 0

    # 往用户评论列表中添加评论数据
    def add_comment_to_user_comment_list(self, user_id, comment_id):
        key = self.get_comment_list_user_id_key(user_id)
        return self.handle.lpushx(key, comment_id)

    # 往资源评论列表中添加评论数据
    def add_comment_to_source_comment_list(self, source_type, source_id, comment_id):
        key = self.get_comment_list_source_id_key(source_type, source_id)
        return self.handle.lpushx(key, comment_id)


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
