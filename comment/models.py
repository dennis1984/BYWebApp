# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models, transaction
from django.utils.timezone import now

from media.models import Media, Information, Case
from users.models import User
from horizon.models import (model_to_dict,
                            get_perfect_filter_params,
                            BaseManager)

import json
import datetime


SOURCE_TYPE_DB = {
    1: Media,         # 资源
    2: Case,          # 案例
    3: Information,   # 资讯
}

COMMENT_OPINION_ACTION = {
    1: 'like',
    2: 'dislike',
}


class Comment(models.Model):
    """
    用户点评
    """
    user_id = models.IntegerField('用户ID', db_index=True)

    # 点评资源类型： 1：资源 2：案例 3：资讯
    source_type = models.IntegerField('点评资源类型', default=1)
    # 资源数据ID
    source_id = models.IntegerField('点评资源ID')
    content = models.CharField('点评内容', max_length=512)

    # 是否被管理员推荐该评论: 0: 否  1：是
    is_recommend = models.IntegerField('是否被管理员推荐', default=0)
    like = models.IntegerField('喜欢数量', default=0)
    dislike = models.IntegerField('不喜欢数量', default=0)

    # 数据状态：1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_comment'
        unique_together = ['user_id', 'source_type', 'source_id', 'status']
        index_together = ['source_type', 'source_id']
        ordering = ['-created']

    def __unicode__(self):
        return '%s:%s:%s' % (self.user_id, self.source_type, self.source_id)

    @property
    def perfect_detail(self):
        is_recommend = self.is_recommend
        reply_message = ''
        if is_recommend:
            reply = ReplyComment.get_object(comment_id=self.pk)
            reply_message = reply.message

        source_ins = self.get_source_object(source_type=self.source_type,
                                            source_id=self.source_id)
        if isinstance(source_ins, Exception):
            return source_ins
        else:
            source_title = source_ins.title

        user = User.get_object(pk=self.user_id)
        user_nickname = ''
        if not isinstance(user, Exception):
            user_nickname = user.nickname

        detail = model_to_dict(self)
        detail['is_recommend'] = is_recommend
        detail['reply_message'] = reply_message
        detail['source_title'] = source_title
        detail['user_nickname'] = user_nickname
        return detail

    @classmethod
    def update_opinion_count(cls, comment_id, action=1):
        comment = None
        if action not in COMMENT_OPINION_ACTION:
            return Exception('Params [action] is incorrect.')
        # 数据库加排它锁，保证更改信息是列队操作的，防止数据混乱
        with transaction.atomic():
            _comment = cls.get_object(pk=comment_id)
            if isinstance(_comment, Exception):
                return _comment

            attr = COMMENT_OPINION_ACTION[action]
            opinion_value = getattr(_comment, attr)
            setattr(_comment, attr, opinion_value + 1)
            _comment.save()
            comment = _comment
        return comment

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def get_detail(cls, **kwargs):
        instance = cls.get_object(**kwargs)
        if isinstance(instance, Exception):
            return instance
        return instance.perfect_detail

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_details(cls, **kwargs):
        instances = cls.filter_objects(**kwargs)
        details = []
        for ins in instances:
            per_detail = ins.perfect_detail
            if isinstance(per_detail, Exception):
                continue
            details.append(ins.perfect_detail)
        return details

    @classmethod
    def get_source_object(cls, source_type, source_id):
        source_class = SOURCE_TYPE_DB.get(source_type)
        if not source_class:
            return Exception('Params is incorrect')

        return source_class.get_object(pk=source_id)

    @classmethod
    def get_comment_count(cls, source_type, source_id):
        """
        获取评论数
        """
        kwargs = {'source_type': source_type, 'source_id': source_id}
        instances = cls.filter_objects(**kwargs)
        if isinstance(instances, Exception):
            return 0
        return len(instances)


class ReplyComment(models.Model):
    """
    管理员回复点评
    """
    comment_id = models.IntegerField(u'被回复点评的记录ID', db_index=True)
    user_id = models.IntegerField('管理员用户ID')
    message = models.TextField('点评回复', null=True, blank=True)

    # 数据状态 1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_reply_comment'
        unique_together = ['comment_id', 'status']

    def __unicode__(self):
        return str(self.comment_id)

    @classmethod
    def get_object(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e


class CommentOpinionRecord(models.Model):
    """
    对用户评论的评价（点赞、踩）的记录
    """
    user_id = models.IntegerField('用户ID', )
    comment_id = models.IntegerField('评论ID')

    # 对评论的操作：1：点赞  2：踩
    action = models.IntegerField('点赞/踩')
    created = models.DateTimeField(default=now)

    class Meta:
        db_table = 'by_comment_opinion_record'
        unique_together = ['user_id', 'comment_id']
        index_together = ['user_id', 'comment_id']

    def __unicode__(self):
        return '%s:%s' % (self.user_id, self.comment_id)

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

