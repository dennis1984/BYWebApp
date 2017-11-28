# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now

from horizon.models import (model_to_dict,
                            get_perfect_filter_params)

import json
import datetime

SCORE_ACTION_DICT = {'comment': {'score': 20,
                                 'action': 1},
                     'download': {'score': 10,
                                  'action': 2}}


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


class ScoreRecord(models.Model):
    """
    积分记录
    """
    user_id = models.IntegerField('用户ID', db_index=True)

    # 积分动作：0：未指定 1：获取积分（发表点评可获得积分）  2：消耗积分（下载报告需要消耗积分）
    action = models.IntegerField('消耗/获取积分', default=0)
    # 消耗/获取积分数量
    score_count = models.IntegerField('积分数量', default=0)
    created = models.DateTimeField('创建时间', default=now)

    class Meta:
        db_table = 'by_score_record'
        ordering = ['-created']

    def __unicode__(self):
        return str(self.user_id)

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


class ScoreAction(object):
    """
    积分操作
       : 增加或减少积分，并添加积分记录
    """
    @classmethod
    def update_score(cls, request, action='comment'):
        score = Score.get_object(user_id=request)
        if isinstance(score, Exception):
            init_data = {'user_id': request.user.id}
            score = Score(**init_data)
            score.save()
        # 评论资源，获得积分
        if action == 'comment':
            score.score += SCORE_ACTION_DICT[action]['score']
        # 下载报告，消耗积分
        elif action == 'download':
            if score.score < SCORE_ACTION_DICT[action]['score']:
                return Exception('Score count is not enough.')
            score.score -= SCORE_ACTION_DICT[action]['score']
        else:
            return Exception('Params [action] is incorrect.')

        score.save()
        return score

    @classmethod
    def create_score_record(cls, request, action='comment'):
        if action not in SCORE_ACTION_DICT:
            return Exception('Params [action] is incorrect.')

        init_data = {'user_id': request.user.id,
                     'action': SCORE_ACTION_DICT[action]['action'],
                     'score_count': SCORE_ACTION_DICT[action]['score']}
        record = ScoreRecord(**init_data)
        record.save()
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

