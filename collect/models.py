# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.db import transaction
from decimal import Decimal

from horizon.models import (model_to_dict,
                            BaseManager,
                            get_perfect_filter_params)

import json
import datetime


class Collect(models.Model):
    """
    用户收藏
    """
    user_id = models.IntegerField('用户ID', db_index=True)
    # 资源类型:  1：案例  2：资源  3：资讯
    source_type = models.IntegerField('收藏类型', default=1)
    # 资源ID
    source_id = models.IntegerField('资源ID')

    # 收藏品状态：1：有效 非1：已取消收藏
    status = models.IntegerField('收藏品状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_collect'
        unique_together = ('user_id', 'source_type', 'source_id', 'status')
        ordering = ['-updated']

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_id, self.source_type, self.source_id)

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e
