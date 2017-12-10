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


MEDIA_PICTURE_PATH = settings.PICTURE_DIRS['web']['media']


def base_get_tags_key_dict(cls):
    """
    获取以资源所属的标签为Key，以案例ID为Value的字典
    """
    instances = cls.filter_objects()
    tags_dict = {}
    for ins in instances:
        try:
            tags = json.loads(ins.tags)
        except:
            continue
        tags = [str(tag) for tag in sorted(tags)]
        tags_key = ':'.join(tags)
        id_list = tags_dict.get(tags_key, [])
        id_list.append(ins.id)
        tags_dict[tags_key] = id_list
    return tags_dict


class Media(models.Model):
    """
    媒体资源
    """
    title = models.CharField('资源标题', max_length=128, db_index=True)
    subtitle = models.CharField('资源副标题', max_length=128, null=True, blank=True)
    description = models.TextField('资源描述/介绍', null=True, blank=True)

    # 资源类型：10：电影 20：电视剧 30：综艺节目
    media_type = models.IntegerField('资源类型', default=10)
    # 题材类别  1：爱情 2：战争 3：校园 4：真人秀
    theme_type = models.IntegerField('题材类别', default=1)
    # 项目进度  1：筹备期 2：策划期 3：xxx
    progress = models.IntegerField('项目进度', default=1)

    # 模板类型 1：模板1  2：模板2
    template_type = models.IntegerField('展示页面模板类型', default=1)
    # # 资源概要展示类型：1：电影、剧集  2：综艺、活动
    # outline_type = models.IntegerField('资源概要展示类型', default=1)

    # 标签：数据格式为JSON字符串，如：['综艺', '植入', '片头']
    tags = models.CharField('资源标签', max_length=256)

    # 资源热度
    temperature = models.FloatField('热度')
    # 票房预测
    box_office_forecast = models.FloatField('票房预测')
    # 口碑预测
    public_praise_forecast = models.FloatField('口碑预测')
    # ROI 投资回报比 例如：1：5 （1比5）
    roi = models.CharField('投入回报比', max_length=10)

    # 资源属性：数据格式为JSON字符串，如：[1, 3, 5] （数字为属性ID）
    # attributes = models.CharField('资源属性', max_length=256, )

    # # 导演：数据格式为JSON字符串，如：['斯皮尔伯格', '冯小刚']
    # director = models.CharField('导演', max_length=256)
    # # 主演：数据格式为JSON字符串，如：['汤姆克鲁斯', '威尔史密斯', '皮尔斯布鲁斯南']
    # stars = models.CharField('主演', max_length=256)
    # # 演员：数据格式为JSON字符串，如：['王晓霞', '詹姆斯', '韦德']
    # actors = models.CharField('演员', max_length=256)
    # # 监制：数据格式为JSON字符串，如：['欧文']
    # producer = models.CharField('监制', max_length=256)
    # # 出品公司：数据格式为JSON字符串，如：['华文映像', '福星传媒']
    # production_company = models.CharField('出品公司', max_length=256)
    #
    # # 预计开机/录制时间
    # recorded_time = models.DateTimeField('开机时间')

    # 资源概述 数据格式为字典形式的JSON字符串，如：{"导演": ["冯小刚", "吴宇森"],
    #                                        "主演": ["成龙", "李连杰"],
    #                                        "出演": ["巩俐", "章子怡"], ......}
    media_outline = models.TextField('资源概述', null=True, blank=True)

    # 预计上映/播出时间
    air_time = models.DateTimeField('播出时间')
    # # 预计播出平台：数据格式为JSON字符串，如：['一线卫视', '视频网络渠道']
    # play_platform = models.CharField('播出平台', max_length=256)

    # 运营标记 0: 未设定 1：热门
    mark = models.IntegerField('运营标记', default=0)

    # 电影表现大数据分析 数据格式为字典形式的JSON字符串，如：{"导演号召力": 3.5,
    #                                                "男主角号召力": 4.0,
    #                                                "女主角号召力": 4.2,
    #                                                "类型关注度": 3.8,
    #                                                "片方指数": 3.7}
    film_performance = models.CharField('电影表现大数据分析', max_length=512, null=True, blank=True)

    picture = models.ImageField('媒体资源原始图片', max_length=200,
                                upload_to=MEDIA_PICTURE_PATH,
                                default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))
    picture_profile = models.ImageField('简介图片', max_length=200,
                                        upload_to=MEDIA_PICTURE_PATH,
                                        default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))
    picture_detail = models.ImageField('详情图片', max_length=200,
                                       upload_to=MEDIA_PICTURE_PATH,
                                       default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))
    # 资源状态：1：正常 非1：已删除
    status = models.IntegerField('资源状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_media'
        ordering = ['-updated']
        unique_together = ['title', 'subtitle', 'status']

    class AdminMeta:
        json_fields = ['tags', 'media_outline', 'film_performance']

    def __unicode__(self):
        return self.title

    def get_perfect_tags(self, tag_ids):
        tag_details = []
        for tag_id in tag_ids:
            tag = ResourceTags.get_object(pk=tag_id)
            if isinstance(tag, Exception):
                continue
            tag_details.append(tag.name)
        return tag_details

    @property
    def perfect_detail(self):
        detail = model_to_dict(self)
        for key in detail.keys():
            if key in self.AdminMeta.json_fields:
                if detail[key]:
                    if key == 'tags':
                        tag_ids = json.loads(detail[key])
                        detail[key] = self.get_perfect_tags(tag_ids)
                    else:
                        detail[key] = json.loads(detail[key])

        media_type_dict = getattr(self, '_media_type_dict', {})
        theme_type_dict = getattr(self, '_theme_type_dict', {})
        progress_dict = getattr(self, '_progress_dict', {})
        media_type_ins = media_type_dict.get(self.media_type)
        if not media_type_ins:
            media_type_ins = MediaType.get_object(pk=self.media_type)
            media_type_dict[self.media_type] = media_type_ins
            setattr(self, '_media_type_dict', media_type_dict)
        theme_type_ins = theme_type_dict.get(self.theme_type)
        if not theme_type_ins:
            theme_type_ins = ThemeType.get_object(pk=self.theme_type)
            theme_type_dict[self.theme_type] = theme_type_ins
            setattr(self, '_theme_type_dict', theme_type_dict)
        progress_ins = progress_dict.get(self.progress)
        if not progress_ins:
            progress_ins = ProjectProgress.get_object(pk=self.progress)
            progress_dict[self.progress] = progress_ins
            setattr(self, '_progress_dict', progress_dict)
        detail['media_type_name'] = getattr(media_type_ins, 'name', None)
        detail['theme_type_name'] = getattr(theme_type_ins, 'name', None)
        detail['progress_name'] = getattr(progress_ins, 'name', None)
        return detail

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

    @classmethod
    def get_tags_key_dict(cls):
        """
        获取以媒体资源所属的标签为Key，以案例ID为Value的字典
        """
        return base_get_tags_key_dict(cls)


class MediaConfigure(models.Model):
    """
    媒体资源属性配置
    """
    media_id = models.IntegerField('媒体资源ID')

    dimension_id = models.IntegerField('所属维度ID', db_index=True)
    attribute_id = models.IntegerField('所属属性ID')

    # 数据状态：1：正常，非1：已删除
    status = models.IntegerField('状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_media_configure'
        index_together = ['dimension_id', 'attribute_id']
        unique_together = ['media_id', 'attribute_id', 'status']

    def __unicode__(self):
        return '%s:%s:%s' % (self.media_id, self.dimension_id, self.attribute_id)

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


class MediaType(models.Model):
    """
    资源类型
    """
    name = models.CharField('资源类型名称', max_length=64, db_index=True)
    sort_order = models.IntegerField('排序顺序', default=0)

    # 数据状态 1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_media_type'
        unique_together = ['name', 'status']
        ordering = ['-updated']

    def __unicode__(self):
        return '%s' % self.name

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
            instances = cls.objects.filter(**kwargs)
        except Exception as e:
            return e
        # 排序
        sort_instances = sorted(instances, key=lambda x: x.sort_order)
        key = -1
        for index, item in enumerate(sort_instances):
            if item.sort_order != 0:
                break
            key = index
        if key == -1:
            return sort_instances
        else:
            new_sort_list = sort_instances[key + 1:]
            new_sort_list.extend(sort_instances[:key + 1])
            return new_sort_list


class ThemeType(models.Model):
    """
    题材类别
    """
    name = models.CharField('题材类别名称', max_length=64)
    media_type_id = models.IntegerField('所属资源类型ID', db_index=True)
    sort_order = models.IntegerField('排序顺序', default=0)

    # 数据状态 1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_theme_type'
        unique_together = ['name', 'media_type_id', 'status']
        ordering = ['media_type_id', '-updated']

    def __unicode__(self):
        return '%s' % self.name

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
            instances = cls.objects.filter(**kwargs)
        except Exception as e:
            return e
        # 排序
        sort_instances = sorted(instances, key=lambda x: x.sort_order)
        key = -1
        for index, item in enumerate(sort_instances):
            if item.sort_order != 0:
                break
            key = index
        if key == -1:
            return sort_instances
        else:
            new_sort_list = sort_instances[key + 1:]
            new_sort_list.extend(sort_instances[:key + 1])
            return new_sort_list


class ProjectProgress(models.Model):
    """
    项目进度
    """
    name = models.CharField('项目进度名称', max_length=64, db_index=True)
    sort_order = models.IntegerField('排序顺序', default=0)

    # 数据状态 1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_project_progress'
        unique_together = ['name', 'status']

    def __unicode__(self):
        return '%s' % self.name

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
            instances = cls.objects.filter(**kwargs)
        except Exception as e:
            return e
        # 排序
        sort_instances = sorted(instances, key=lambda x: x.sort_order)
        key = -1
        for index, item in enumerate(sort_instances):
            if item.sort_order != 0:
                break
            key = index
        if key == -1:
            return sort_instances
        else:
            new_sort_list = sort_instances[key + 1:]
            new_sort_list.extend(sort_instances[:key + 1])
            return new_sort_list


class ResourceTags(models.Model):
    """
    资源标签
    """
    name = models.CharField('标签名字', max_length=64, db_index=True)
    description = models.CharField('描述', max_length=256, null=True, blank=True)

    # 数据状态：1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_resource_tag'
        ordering = ['-updated']
        unique_together = ['name', 'status']

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


INFORMATION_FILE_PATH = settings.PICTURE_DIRS['web']['information']


class Information(models.Model):
    """
    资讯
    """
    title = models.CharField('标题', max_length=128, db_index=True)
    subtitle = models.CharField('副标题', max_length=128, null=True, blank=True)
    description = models.TextField('描述/介绍', null=True, blank=True)

    content = models.TextField('正文')
    picture = models.ImageField('封面图', max_length=200,
                                upload_to=MEDIA_PICTURE_PATH,
                                default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))

    # 标签：数据格式为JSON字符串，如：['综艺', '植入', '片头']
    tags = models.CharField('标签', max_length=256)
    # 浏览数
    read_count = models.IntegerField('浏览数', default=0)
    # 点赞数量
    like = models.IntegerField('点赞数量', default=0)
    # 收藏数量
    collection_count = models.IntegerField('收藏数量', default=0)
    # 数据状态：1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)

    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_information'

    class AdminMeta:
        json_fields = ['tags']

    def __unicode__(self):
        return self.title

    def get_perfect_tags(self, tag_ids):
        tag_details = []
        for tag_id in tag_ids:
            tag = ResourceTags.get_object(pk=tag_id)
            if isinstance(tag, Exception):
                continue
            tag_details.append(tag.name)
        return tag_details

    @property
    def perfect_detail(self):
        detail = model_to_dict(self)
        for key in detail.keys():
            if key in self.AdminMeta.json_fields:
                if key == 'tags':
                    tag_ids = json.loads(detail[key])
                    detail[key] = self.get_perfect_tags(tag_ids)
                else:
                    detail[key] = json.loads(detail[key])
        return detail

    @classmethod
    def plus_action(cls, information_id, attr='read_count'):
        information = None
        attr_keys = ['read_count', 'like', 'collection_count']

        if attr not in attr_keys:
            return Exception('Params [attr] is incorrect.')
        # 数据库加排它锁，保证更改信息是列队操作的，防止数据混乱
        with transaction.atomic():
            _information = cls.get_object(pk=information_id)
            if isinstance(_information, Exception):
                return _information

            opinion_value = getattr(_information, attr)
            setattr(_information, attr, opinion_value + 1)
            _information.save()
            information = _information
        return information

    @classmethod
    def reduce_action(cls, information_id, attr='collection_count'):
        information = None
        attr_keys = ['like', 'collection_count']

        if attr not in attr_keys:
            return Exception('Params [attr] is incorrect.')
        # 数据库加排它锁，保证更改信息是列队操作的，防止数据混乱
        with transaction.atomic():
            _information = cls.get_object(pk=information_id)
            if isinstance(_information, Exception):
                return _information

            opinion_value = getattr(_information, attr)
            setattr(_information, attr, opinion_value - 1)
            _information.save()
            information = _information
        return information

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

    @classmethod
    def get_tags_key_dict(cls):
        """
        获取以资讯所属的标签为Key，以案例ID为Value的字典
        """
        return base_get_tags_key_dict(cls)


CASE_FILE_PATH = settings.PICTURE_DIRS['web']['case']


class Case(models.Model):
    """
    案例
    """
    title = models.CharField('标题', max_length=128, db_index=True)
    subtitle = models.CharField('副标题', max_length=128, null=True, blank=True)
    description = models.TextField('描述/介绍', null=True, blank=True)

    content = models.TextField('正文')
    picture = models.ImageField('封面图', max_length=200,
                                upload_to=MEDIA_PICTURE_PATH,
                                default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))

    # 标签：数据格式为JSON字符串，如：['综艺', '植入', '片头']
    tags = models.CharField('标签', max_length=256)
    # 浏览数
    read_count = models.IntegerField('浏览数', default=0)
    # 点赞数量
    like = models.IntegerField('点赞数量', default=0)
    # 收藏数量
    collection_count = models.IntegerField('收藏数量', default=0)
    # 数据状态：1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)

    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_case'

    class AdminMeta:
        json_fields = ['tags']

    def __unicode__(self):
        return self.title

    def get_perfect_tags(self, tag_ids):
        tag_details = []
        for tag_id in tag_ids:
            tag = ResourceTags.get_object(pk=tag_id)
            if isinstance(tag, Exception):
                continue
            tag_details.append(tag.name)
        return tag_details

    @property
    def perfect_detail(self):
        detail = model_to_dict(self)
        for key in detail.keys():
            if key in self.AdminMeta.json_fields:
                if key == 'tags':
                    tag_ids = json.loads(detail[key])
                    detail[key] = self.get_perfect_tags(tag_ids)
                else:
                    detail[key] = json.loads(detail[key])
        return detail

    @classmethod
    def plus_action(cls, case_id, attr='read_count'):
        case = None
        attr_keys = ['read_count', 'like', 'collection_count']

        if attr not in attr_keys:
            return Exception('Params [attr] is incorrect.')
        # 数据库加排它锁，保证更改信息是列队操作的，防止数据混乱
        with transaction.atomic():
            _case = cls.get_object(pk=case_id)
            if isinstance(_case, Exception):
                return _case

            opinion_value = getattr(_case, attr)
            setattr(_case, attr, opinion_value + 1)
            _case.save()
            case = _case
        return case

    @classmethod
    def reduce_action(cls, information_id, attr='collection_count'):
        information = None
        attr_keys = ['like', 'collection_count']

        if attr not in attr_keys:
            return Exception('Params [attr] is incorrect.')
        # 数据库加排它锁，保证更改信息是列队操作的，防止数据混乱
        with transaction.atomic():
            _information = cls.get_object(pk=information_id)
            if isinstance(_information, Exception):
                return _information

            opinion_value = getattr(_information, attr)
            setattr(_information, attr, opinion_value - 1)
            _information.save()
            information = _information
        return information

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

    @classmethod
    def get_tags_key_dict(cls):
        """
        获取以案例所属的标签为Key，以案例ID为Value的字典
        """
        return base_get_tags_key_dict(cls)


class ResourceOpinionRecord(models.Model):
    """
    资源文件点赞记录
    """
    user_id = models.IntegerField('用户ID')
    source_type = models.IntegerField('媒体资源类型')
    source_id = models.IntegerField('媒体资源ID')

    # 资源文件操作：1：点赞  2：踩
    action = models.IntegerField('操作（点赞、踩）', default=1)
    created = models.DateTimeField('创建时间', default=now)

    class Meta:
        db_table = 'by_resource_opinion_record'
        unique_together = ['user_id', 'source_type', 'source_id']
        index_together = ('user_id', 'source_type', 'source_id')

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


ADVERT_PICTURE_PATH = settings.PICTURE_DIRS['web']['advert']


class AdvertResource(models.Model):
    """
    广告资源
    """
    title = models.CharField('广告标题', max_length=128)
    subtitle = models.CharField('广告副标题', max_length=128, null=True, blank=True)
    # 点评资源类型： 1：资源 2：案例 3：资讯
    source_type = models.IntegerField('媒体资源类型')

    link_url = models.TextField('链接地址', null=True, blank=True)
    picture = models.ImageField(max_length=200,
                                upload_to=ADVERT_PICTURE_PATH,
                                default=os.path.join(ADVERT_PICTURE_PATH, 'noImage.png'))
    # 数据状态：1：有效 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_advert_resource'
        index_together = ('title',)

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
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e


SOURCE_TYPE_DB = {
    1: Media,         # 资源
    2: Case,          # 案例
    3: Information,   # 资讯
}


class SourceModelAction(object):
    """
    资源点赞、增加浏览数等操作
    """
    @classmethod
    def get_source_object(cls, source_type, source_id):
        if source_type not in SOURCE_TYPE_DB:
            return Exception('Params [resource_type] is incorrect.')

        source_class = SOURCE_TYPE_DB[source_type]
        return source_class.get_object(pk=source_id)

    @classmethod
    def update_read_count(cls, source_type, source_id):
        if source_type not in SOURCE_TYPE_DB:
            return Exception('Params [resource_type] is incorrect.')

        source_class = SOURCE_TYPE_DB[source_type]
        return source_class.plus_action(source_id, 'read_count')

    @classmethod
    def update_like_count(cls, source_type, source_id):
        if source_type not in SOURCE_TYPE_DB:
            return Exception('Params [resource_type] is incorrect.')

        source_class = SOURCE_TYPE_DB[source_type]
        return source_class.plus_action(source_id, 'like')

    @classmethod
    def update_collection_count(cls, source_type, source_id, method='plus'):
        if source_type not in SOURCE_TYPE_DB:
            return Exception('Params [resource_type] is incorrect.')
        if method not in ['plus', 'reduce']:
            return Exception('Params [resource_type] is incorrect.')

        source_class = SOURCE_TYPE_DB[source_type]
        if method == 'plus':
            return source_class.plus_action(source_id, 'collection_count')
        else:
            return source_class.reduce_action(source_id, 'collection_count')

    @classmethod
    def create_like_record(cls, request, source_type, source_id):
        # source_ins = cls.get_source_object(source_type, source_id)
        # if isinstance(source_ins, Exception):
        #     return source_ins
        init_data = {'user_id': request.user.id,
                     'source_type': source_type,
                     'source_id': source_id}
        record = ResourceOpinionRecord(**init_data)
        try:
            record.save()
        except Exception as e:
            return e
        return record

    @classmethod
    def like_action(cls, request, source_type, source_id):
        record = cls.create_like_record(request, source_type, source_id)
        if isinstance(record, Exception):
            return record
        source_ins = cls.update_like_count(source_type, source_id)
        if isinstance(source_ins, Exception):
            return source_ins
        return record, source_ins

