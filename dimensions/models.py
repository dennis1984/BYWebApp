# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.db import transaction
from decimal import Decimal

from horizon.models import (model_to_dict,
                            BaseManager,
                            get_perfect_filter_params)

import json
import datetime
import os


class Dimension(models.Model):
    """
    维度
    """
    name = models.CharField('维度名称', max_length=32, unique=True, db_index=True)
    description = models.CharField('维度描述', max_length=256, null=True, blank=True)

    # 资源状态：1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_dimension'
        # unique_together = ('user_id', 'dishes_id', 'status')
        ordering = ['-update']

    def __unicode__(self):
        return self.name

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


class Attribute(models.Model):
    """
    属性
    """
    name = models.CharField('属性名称', max_length=64, unique=True, db_index=True)
    dimension_id = models.IntegerField('所属维度ID')

    # 资源状态：1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_attribute'
        ordering = ['-update']

    def __unicode__(self):
        return self.name

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


class Tag(models.Model):
    """
    标签
    """
    name = models.CharField('标签名称', max_length=64, unique=True, db_index=True)

    attribute_id = models.IntegerField('匹配属性ID')
    match_value = models.FloatField('与属性匹配值', default=1.0)

    # 资源状态：1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_tag'
        ordering = ['-update']

    def __unicode__(self):
        return self.name

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
