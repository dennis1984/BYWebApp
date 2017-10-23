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
    def __init__(self, request, instance=None, data=None, **kwargs):
        if data:
            data['user_id'] = request.user.id
            super(CommentSerializer, self).__init__(data=data, **kwargs)
        else:
            super(CommentSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Comment
        fields = '__all__'


class CommentDetailSerializer(BaseSerializer):
    user_id = serializers.IntegerField()
    source_type = serializers.IntegerField()
    source_id = serializers.IntegerField()

    content = serializers.CharField()
    like = serializers.IntegerField()
    dislike = serializers.IntegerField()
    is_recommend = serializers.IntegerField()

    created = serializers.DateTimeField()


class CommentListSerializer(BaseListSerializer):
    child = CommentDetailSerializer()
