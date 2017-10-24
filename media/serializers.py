# -*- coding:utf8 -*-
from rest_framework import serializers

from media.models import Media, ResourceTags
from horizon.serializers import (BaseSerializer,
                                 BaseModelSerializer,
                                 BaseListSerializer)
from horizon.decorators import has_permission_to_update

import os


class MediaSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            super(MediaSerializer, self).__init__(data=data, **kwargs)
        else:
            super(MediaSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Media
        fields = '__all__'

    @has_permission_to_update
    def delete(self, request, instance):
        validated_data = {'status': instance.id + 1}
        return super(MediaSerializer, self).update(instance, validated_data)


class ResourceTagsDetailSerializer(BaseModelSerializer):
    class Meta:
        model = ResourceTags
        fields = '__all__'


class ResourceTagsListSerializer(BaseListSerializer):
    child = ResourceTagsDetailSerializer()
