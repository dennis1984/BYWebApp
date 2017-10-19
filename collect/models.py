# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.db import transaction
from decimal import Decimal

from horizon.models import model_to_dict

import json
import datetime


class CollectManager(models.Manager):
    def get(self, *args, **kwargs):
        object_data = super(CollectManager, self).get(status=1, *args, **kwargs)
        return object_data

    def filter(self, *args, **kwargs):
        object_data = super(CollectManager, self).filter(status=1, *args, **kwargs)
        return object_data


class Collect(models.Model):
    """
    用户收藏
    """
    user_id = models.IntegerField('用户ID', db_index=True)
    # 收藏类型：0：未指定  1：案例  2：资源  3：资讯
    type = models.IntegerField('收藏类型', default=0)
    # 收藏品ID
    collection_id = models.IntegerField('收藏品ID')

    # 收藏品状态：1：有效 非：已取消收藏
    status = models.IntegerField('收藏品状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = CollectManager()

    class Meta:
        db_table = 'by_collect'
        unique_together = ('user_id', 'type', 'status')
        ordering = ['-created']

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_id, self.type, self.collection_id)

    @classmethod
    def is_collected(cls, request, dishes_id):
        kwargs = {'user_id': request.user.id,
                  'dishes_id': dishes_id}
        result = cls.get_object(**kwargs)
        if isinstance(result, Exception):
            return False
        return True

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def get_collect_list_with_user(cls, request):
        kwargs = {'user_id': request.user.id}
        return cls.filter_objects(**kwargs)
