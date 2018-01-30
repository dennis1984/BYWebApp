# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.conf import settings

from media.models import Media, ResourceTags
from media.caches import MediaCache
from horizon.models import (model_to_dict,
                            BaseManager,
                            get_perfect_filter_params)

import json
import datetime
import os


REPORT_PICTURE_PATH = settings.PICTURE_DIRS['web']['report']


class Report(models.Model):
    """
    报告
    """
    title = models.CharField('报告标题', max_length=32)
    subtitle = models.CharField('报告副标题', max_length=128, null=True, blank=True)
    description = models.TextField('报告描述', null=True, blank=True)

    media_id = models.IntegerField('所属资源ID', db_index=True)
    # 标签：数据格式为JSON字符串，如：['行业月报', '综艺']
    tags = models.CharField('标签', max_length=256)
    report_file = models.FileField('报告文件', max_length=200,
                                   upload_to=REPORT_PICTURE_PATH,
                                   default=os.path.join(REPORT_PICTURE_PATH, 'noImage.png')
                                   )
    # 数据状态：1：正常  非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField(default=now)
    updated = models.DateTimeField(auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_report'
        unique_together = ('media_id', 'status')
        ordering = ['-updated']

    class AdminMeta:
        json_fields = ['tags']

    def __unicode__(self):
        return self.title

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
        if isinstance(instances, Exception):
            return instances

        details = []
        for ins in instances:
            details.append(ins.perfect_detail)
        return details

    @property
    def perfect_detail(self):
        detail = model_to_dict(self)
        if hasattr(self, 'AdminMeta'):
            if hasattr(self.AdminMeta, 'json_fields'):
                for field in self.AdminMeta.json_fields:
                    if field == 'tags':
                        tag_ids = json.loads(detail[field])
                        detail[field] = self.get_perfect_tags(tag_ids)
                    else:
                        detail[field] = json.loads(detail[field])

        media = MediaCache().get_media_by_id(self.media_id)
        if isinstance(media, Exception):
            return media
        detail['media_picture'] = media.picture
        return detail

    def get_perfect_tags(self, tag_ids):
        tag_names = []
        for tag_id in tag_ids:
            tag = ResourceTags.get_object(pk=tag_id)
            if isinstance(tag, Exception):
                continue
            tag_names.append(tag.name)
        return tag_names


class ReportDownloadRecord(models.Model):
    """
    报告下载记录
    """
    report_id = models.IntegerField('报告ID', db_index=True)
    user_id = models.IntegerField('用户ID')

    created = models.DateTimeField('下载时间', default=now)

    class Meta:
        db_table = 'by_report_download_record'
        unique_together = ['report_id', 'user_id']
        ordering = ['-created']

    def __unicode__(self):
        return '%s:%s' % (self.report_id, self.user_id)

    @property
    def perfect_detail(self):
        report_detail = Report.get_detail(pk=self.report_id)
        if isinstance(report_detail, Exception):
            return report_detail
        detail = model_to_dict(self)
        for pop_key in ['created', 'updated']:
            report_detail.pop(pop_key)
        detail.update(**report_detail)
        return detail

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
    def filter_details(cls, **kwargs):
        instances = cls.filter_objects(**kwargs)
        if isinstance(instances, Exception):
            return instances

        details = []
        for ins in instances:
            perfect_detail = ins.perfect_detail
            if isinstance(perfect_detail, Exception):
                continue
            details.append(perfect_detail)
        return details
