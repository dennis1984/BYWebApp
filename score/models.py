# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now

from horizon.models import model_to_dict, get_perfect_detail_by_detail

import json
import datetime


class Score(models.Model):
    """
    用户积分
    """
    user_id = models.IntegerField('用户ID', unique=True, db_index=True)
    score = models.IntegerField('积分', default=0)

    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'by_score'

    def __unicode__(self):
        return '%s' % self.user_id

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


class ScoreRecord(models.Model):
    """
    积分记录
    """
    user_id = models.IntegerField('用户ID')

    # 积分动作：0：未指定 1：获取积分（发表点评可获得积分）  2：消耗积分（下载报告需要消耗积分）
    action = models.IntegerField('消耗/获取积分', default=0)
    created = models.DateTimeField('创建时间', default=now)

    class Meta:
        db_table = 'by_score_record'
        ordering = ['-created']

    def __unicode__(self):
        return str(self.user_id)

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e
