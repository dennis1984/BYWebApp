# -*- coding:utf8 -*-
from rest_framework import serializers
from horizon.decorators import has_permission_to_update
from horizon.serializers import (BaseSerializer,
                                 BaseModelSerializer,
                                 BaseListSerializer)
from horizon.main import make_random_number_of_string
from horizon.decorators import has_permission_to_update

import json
import os


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
