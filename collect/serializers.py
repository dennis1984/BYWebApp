# -*- coding:utf8 -*-
from collect.models import Collect
from horizon.decorators import has_permission_to_update
from horizon.serializers import (BaseSerializer,
                                 BaseModelSerializer,
                                 BaseListSerializer)
from rest_framework import serializers

from horizon.main import make_random_number_of_string
from horizon.decorators import has_permission_to_update
from media.caches import SourceModelAction

import os


class CollectSerializer(BaseModelSerializer):
    def __init__(self, request, instance=None, data=None, **kwargs):
        if data:
            data['user_id'] = request.user.id
            super(CollectSerializer, self).__init__(data=data, **kwargs)
        else:
            super(CollectSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Collect
        fields = '__all__'

    def save(self, **kwargs):
        # 增加资源的收藏数量
        SourceModelAction.update_collection_count(kwargs['source_type'], kwargs['source_id'])
        return super(CollectSerializer, self).save(**kwargs)

    def delete(self, instance):
        # 减少资源的收藏数量
        SourceModelAction.update_collection_count(instance.source_type, instance.source_id,
                                                  method='reduce')
        validated_data = {'status': instance.id + 1}
        return super(CollectSerializer, self).update(instance, validated_data)


class CollectDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    source_type = serializers.IntegerField()
    source_id = serializers.IntegerField()
    source_title = serializers.CharField()
    source_description = serializers.CharField(allow_blank=True, allow_null=True)
    tags = serializers.ListField()
    updated = serializers.DateTimeField()


class CollectListSerializer(BaseListSerializer):
    child = CollectDetailSerializer()
