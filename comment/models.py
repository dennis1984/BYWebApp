# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now

from horizon.models import (model_to_dict,
                            get_perfect_filter_params,
                            BaseManager)

import json
import datetime


class Comment(models.Model):
    """
    用户点评
    """
    user_id = models.IntegerField('用户ID')

    # 点评资源类型： 1：资源 2：案例 3：资讯
    source_type = models.IntegerField('点评资源类型', default=1)
    # 资源数据ID
    source_id = models.IntegerField('点评资源ID')
    content = models.CharField('点评内容', max_length=512)

    reply_id = models.IntegerField('管理员回复评论ID', null=True)
    like = models.IntegerField('喜欢数量', default=0)
    dislike = models.IntegerField('不喜欢数量', default=0)

    # 数据状态：1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)

    objects = BaseManager()

    class Meta:
        db_table = 'by_comment'
        unique_together = ['user_id', 'source_type', 'source_id']
        index_together = ['source_type', 'source_id']
        ordering = ['-created']

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


class ReplyComment(models.Model):
    """
    管理员回复点评
    """
    comment_id = models.IntegerField(u'被回复点评的记录ID', unique=True)
    user_id = models.IntegerField('管理员用户ID')

    messaged = models.TextField('评价留言', null=True, blank=True)
    created = models.DateTimeField('创建时间', default=now)

    class Meta:
        db_table = 'by_reply_comment'

    def __unicode__(self):
        return str(self.comment_id)

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e
