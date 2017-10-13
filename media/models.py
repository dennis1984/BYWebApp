# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.db import transaction
from decimal import Decimal

from horizon.models import model_to_dict, BaseManager

import json
import datetime
import os


MEDIA_PICTURE_PATH = settings.PICTURE_DIRS['web']['media']


class Media(models.Model):
    """
    媒体资源
    """
    title = models.CharField('资源标题', max_length=32, db_index=True)
    subtitle = models.CharField('资源副标题', max_length=128, null=True, blank=True)
    description = models.CharField('资源描述', max_length=256, null=True, blank=True)

    # 资源类型：10：电影 20：电视剧 30：综艺节目
    media_type = models.IntegerField('资源类型', default=10)
    # 题材类别  1：爱情 2：战争 3：校园 4：真人秀
    theme_type = models.IntegerField('题材类别', default=1)
    # 项目进度  1：筹备期 2：策划期 3：xxx
    progress = models.IntegerField('项目进度', default=1)

    # 导演：数据格式为JSON字符串，如：['斯皮尔伯格', '冯小刚']
    director = models.CharField('导演', max_length=256)
    # 主演：数据格式为JSON字符串，如：['汤姆克鲁斯', '威尔史密斯', '皮尔斯布鲁斯南']
    stars = models.CharField('主演', max_length=256)

    recorded_time = models.DateTimeField('开机时间')
    air_time = models.DateTimeField('播出时间')

    picture_profile = models.ImageField('简介图片', max_length=200,
                                        upload_to=MEDIA_PICTURE_PATH,
                                        default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))
    picture_detail = models.ImageField('详情图片', max_length=200,
                                       upload_to=MEDIA_PICTURE_PATH,
                                       default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))
    picture_hd = models.ImageField('高清图片', max_length=200,
                                   upload_to=MEDIA_PICTURE_PATH,
                                   default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))
    # 资源状态：1：正常 非1：已删除
    status = models.IntegerField('资源状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_collect'
        unique_together = ('user_id', 'dishes_id', 'status')
        ordering = ['-created']

    def __unicode__(self):
        return self.title

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
