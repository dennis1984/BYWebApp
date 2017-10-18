# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now

from horizon.models import model_to_dict, get_perfect_detail_by_detail

import json
import datetime


class Comment(models.Model):
    """
    用户点评
    """
    user_id = models.IntegerField('用户ID')
    media_id = models.IntegerField('媒体资源ID', db_index=True)
    content = models.CharField('点评内容', max_length=512)

    reply_id = models.IntegerField('管理员回复评论ID', null=True)
    created = models.DateTimeField('创建时间', default=now)

    class Meta:
        db_table = 'by_comment'

    def __unicode__(self):
        return '%s:%s' % (self.user_id, self.media_id)

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


class ReplyComment(models.Model):
    """
    管理员回复点评
    """
    comment_id = models.IntegerField(u'被回复点评的记录ID', unique=True, db_index=True)
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
