# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.db import transaction
from decimal import Decimal

from comment.models import SOURCE_TYPE_DB
from media.models import Media
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
    # 媒体资源类型:  1：资源  2：案例  3：资讯
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

    @classmethod
    def get_source_object(cls, source_type, source_id):
        source_class = SOURCE_TYPE_DB.get(source_type)
        if not source_class:
            return Exception('Params is incorrect')

        return source_class.get_detail(pk=source_id)

    @classmethod
    def filter_details(cls, **kwargs):
        instances = cls.filter_objects(**kwargs)
        details = []
        for ins in instances:
            source_detail = cls.get_source_object(source_type=ins.source_type,
                                                  source_id=ins.source_id)
            if isinstance(source_detail, Exception):
                continue
            item_dict = model_to_dict(ins)
            item_dict['source_title'] = source_detail['title']
            item_dict['source_description'] = source_detail['description']
            item_dict['updated'] = source_detail['created']
            item_dict['tags'] = source_detail['tags']
            item_dict['picture'] = source_detail['picture']
            details.append(item_dict)
        return details

    @classmethod
    def get_collection_count(cls, source_type, source_id):
        """
        获取收藏数
        """
        kwargs = {'source_type': source_type, 'source_id': source_id}
        instances = cls.filter_objects(**kwargs)
        if isinstance(instances, Exception):
            return 0
        return len(instances)
