# -*- coding:utf8 -*-
from rest_framework import serializers

from dimensions.models import (Dimension, Attribute, Tag, TagConfigure)
from media.models import MediaConfigure, Media
from horizon.decorators import has_permission_to_update
from horizon.serializers import (BaseSerializer,
                                 BaseModelSerializer,
                                 BaseListSerializer)
from horizon.main import make_random_number_of_string

import os


class DimensionSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            super(DimensionSerializer, self).__init__(data=data, **kwargs)
        else:
            super(DimensionSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Dimension
        fields = '__all__'


class DimensionListSerializer(BaseListSerializer):
    child = DimensionSerializer()


class TagSerializer(BaseModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TagListSerializer(BaseListSerializer):
    child = TagSerializer()


class MediaSerializer(BaseModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'


class MediaListSerializer(BaseListSerializer):
    child = MediaSerializer()


class MatchActionSerializer(BaseSerializer):
    match_degree = serializers.FloatField()
    data = serializers.DictField()


class MatchActionListSerializer(BaseListSerializer):
    child = MatchActionSerializer()

