# -*- coding:utf8 -*-
from rest_framework import serializers

from score.models import Score, ScoreRecord
from horizon.decorators import has_permission_to_update
from horizon.serializers import (BaseSerializer,
                                 BaseModelSerializer,
                                 BaseListSerializer)
from horizon.main import make_random_number_of_string
from horizon.decorators import has_permission_to_update

import json
import os


class ScoreSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            super(ScoreSerializer, self).__init__(data=data, **kwargs)
        else:
            super(ScoreSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Score
        fields = '__all__'


class ScoreRecordDetailSerializer(BaseModelSerializer):
    class Meta:
        model = ScoreRecord
        fields = '__all__'


class ScoreRecordListSerializer(BaseListSerializer):
    child = ScoreRecordDetailSerializer()
