# -*- coding:utf8 -*-
from rest_framework import serializers

from media.models import Media, ResourceTags
from horizon.serializers import (BaseSerializer,
                                 BaseModelSerializer,
                                 BaseListSerializer)
from horizon.decorators import has_permission_to_update
from media.models import (MediaType,
                          ThemeType,
                          ProjectProgress,
                          Media,
                          AdvertResource)

import os


class MediaTypeSerializer(BaseModelSerializer):
    class Meta:
        model = MediaType
        fields = '__all__'


class MediaTypeListSerailizer(BaseListSerializer):
    child = MediaTypeSerializer()


class ThemeTypeSerializer(BaseModelSerializer):
    class Meta:
        model = ThemeType
        fields = '__all__'


class ThemeTypeListSerializer(BaseListSerializer):
    child = ThemeTypeSerializer()


class ProgressSerializer(BaseModelSerializer):
    class Meta:
        model = ProjectProgress
        fields = '__all__'


class ProgressListSerializer(BaseListSerializer):
    child = ProgressSerializer()


class MediaDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)

    # 资源类型：10：电影 20：电视剧 30：综艺节目
    media_type = serializers.IntegerField()
    media_type_name = serializers.CharField(allow_null=True, allow_blank=True)
    # 题材类别  1：爱情 2：战争 3：校园 4：真人秀
    theme_type = serializers.IntegerField()
    theme_type_name = serializers.CharField(allow_null=True, allow_blank=True)
    # 项目进度  1：筹备期 2：策划期 3：xxx
    progress = serializers.IntegerField()
    progress_name = serializers.CharField(allow_null=True, allow_blank=True)

    # 模板类型 1：模板1  2：模板2
    template_type = serializers.IntegerField()
    # 标签：数据格式为JSON字符串，如：['综艺', '植入', '片头']
    tags = serializers.ListField()

    # 资源热度
    temperature = serializers.FloatField()
    # 票房预测
    box_office_forecast = serializers.FloatField()
    # 口碑预测
    public_praise_forecast = serializers.FloatField()
    # ROI 投资回报比 例如：1：5 （1比5）
    roi = serializers.CharField()

    # 资源概述 数据格式为字典形式的JSON字符串，如：{"导演": ["冯小刚", "吴宇森"],
    #                                        "主演": ["成龙", "李连杰"],
    #                                        "出演": ["巩俐", "章子怡"], ......}
    media_outline = serializers.DictField(allow_null=True)

    # 预计上映/播出时间
    air_time = serializers.DateTimeField()

    # 运营标记 0: 未设定 1：热门
    mark = serializers.IntegerField()
    # 浏览数
    read_count = serializers.IntegerField(default=0)
    # 点赞数量
    like = serializers.IntegerField(default=0)
    # 收藏数量
    collection_count = serializers.IntegerField(default=0)
    # 评论数量
    comment_count = serializers.IntegerField(default=0)

    # 电影表现大数据分析 数据格式为字典形式的JSON字符串，如：{"导演号召力": 3.5,
    #                                                "男主角号召力": 4.0,
    #                                                "女主角号召力": 4.2,
    #                                                "类型关注度": 3.8,
    #                                                "片方指数": 3.7}
    film_performance = serializers.DictField(allow_null=True)

    # 媒体资源类型  1: 媒体资源  2：案例   3：资讯
    source_type = serializers.IntegerField(default=1)

    picture_profile = serializers.ImageField()
    picture_detail = serializers.ImageField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class MediaListSerializer(BaseListSerializer):
    child = MediaDetailSerializer()


class InformationDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)

    # 资讯正文
    content = serializers.CharField()
    # 封面图
    picture = serializers.ImageField()
    # 标签：数据格式为JSON字符串，如：['综艺', '植入', '片头']
    tags = serializers.ListField(allow_null=True)
    # 浏览数
    read_count = serializers.IntegerField(default=0)
    # 点赞数
    like = serializers.IntegerField(default=0)
    # 收藏数量
    collection_count = serializers.IntegerField(default=0)
    # 评论数量
    comment_count = serializers.IntegerField(default=0)
    # 媒体资源类型  1: 媒体资源  2：案例   3：资讯
    source_type = serializers.IntegerField(default=3)

    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class InformationListSerializer(BaseListSerializer):
    child = InformationDetailSerializer()


class CaseDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)

    # 案例正文
    content = serializers.CharField()
    # 封面图
    picture = serializers.ImageField()
    # 标签：数据格式为JSON字符串，如：['综艺', '植入', '片头']
    tags = serializers.ListField(allow_null=True)
    # 浏览数
    read_count = serializers.IntegerField(default=0)
    # 点赞数
    like = serializers.IntegerField(default=0)
    # 收藏数量
    collection_count = serializers.IntegerField(default=0)
    # 评论数量
    comment_count = serializers.IntegerField(default=0)
    # 媒体资源类型  1: 媒体资源  2：案例   3：资讯
    source_type = serializers.IntegerField(default=2)

    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class CaseListSerializer(BaseListSerializer):
    child = CaseDetailSerializer()


class AdvertResourceSerializer(BaseSerializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_null=True, allow_blank=True)
    # 点评资源类型： 1：资源 2：案例 3：资讯
    source_type = serializers.IntegerField()

    link_url = serializers.CharField(allow_null=True, allow_blank=True)
    picture = serializers.ImageField(allow_null=True)
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class AdvertResourceListSerializer(BaseListSerializer):
    child = AdvertResourceSerializer()


class ResourceDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)

    # 简介图片
    picture = serializers.ImageField()
    # 标签：数据格式为JSON字符串，如：['综艺', '植入', '片头']
    tags = serializers.ListField(allow_null=True)
    # 资源热度
    temperature = serializers.FloatField(required=False)
    # 项目进度  1：筹备期 2：策划期 3：xxx
    progress = serializers.IntegerField(required=False)
    progress_name = serializers.CharField(allow_null=True, allow_blank=True)
    # 浏览数
    read_count = serializers.IntegerField(default=0)
    # 点赞数
    like = serializers.IntegerField(default=0)
    # 收藏数量
    collection_count = serializers.IntegerField(default=0)
    # 评论数量
    comment_count = serializers.IntegerField(default=0)
    # 媒体资源类型  1: 媒体资源  2：案例   3：资讯
    source_type = serializers.IntegerField(default=2)

    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()


class ResourceListSerializer(BaseListSerializer):
    child = ResourceDetailSerializer()
