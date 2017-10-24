# -*- coding:utf8 -*-
from rest_framework import serializers
from comment.models import Comment
from horizon.decorators import has_permission_to_update
from horizon.serializers import (BaseSerializer,
                                 BaseModelSerializer,
                                 BaseListSerializer)
from horizon.main import make_random_number_of_string
from horizon.decorators import has_permission_to_update

import json
import os


class CommentSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            super(CommentSerializer, self).__init__(data=data, **kwargs)
        else:
            super(CommentSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Comment
        fields = '__all__'

    def save(self, **kwargs):
        try:
            return super(CommentSerializer, self).save(**kwargs)
        except Exception as e:
            return e


class ReportDetailSerializer(BaseSerializer):
    user_id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)
    media_id = serializers.IntegerField()
    tags = serializers.ListField()
    report_file = serializers.FileField()
    created = serializers.DateTimeField()


class ReportListSerializer(BaseListSerializer):
    child = ReportDetailSerializer()
