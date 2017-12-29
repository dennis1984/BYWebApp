# -*- coding:utf8 -*-
from rest_framework import serializers
from horizon.decorators import has_permission_to_update
from horizon.serializers import (BaseSerializer,
                                 BaseModelSerializer,
                                 BaseListSerializer)
from horizon.main import make_random_number_of_string
from horizon.decorators import has_permission_to_update

from reports.models import ReportDownloadRecord
from reports.caches import ReportCache

import json
import os


class ReportDetailSerializer(BaseSerializer):
    user_id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)
    media_id = serializers.IntegerField()
    tags = serializers.ListField()
    # report_file = serializers.FileField()
    created = serializers.DateTimeField()


class ReportListSerializer(BaseListSerializer):
    child = ReportDetailSerializer()


class ReportDownloadRecordSerializer(BaseModelSerializer):
    def __int__(self, instance=None, data=None, request=None, **kwargs):
        if data:
            user_id = request.user.id
            data['report_id'] = data.pop('media_id')
            data['user_id'] = user_id
            super(ReportDownloadRecordSerializer, self).__init__(data=data, **kwargs)
        else:
            super(ReportDownloadRecordSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = ReportDownloadRecord
        fields = '__all__'

    def save(self, **kwargs):
        instance = super(ReportDownloadRecordSerializer, self).save(**kwargs)
        # 更新缓存
        ReportCache().insert_data_to_report_download_record(instance.user_id, instance.perfect_detail)
        return instance
