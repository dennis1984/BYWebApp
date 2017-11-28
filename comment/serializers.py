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

    def delete(self, instance):
        validated_data = {'status': instance.id + 1}
        return super(CommentSerializer, self).update(instance, validated_data)


class CommentDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    source_type = serializers.IntegerField()
    source_id = serializers.IntegerField()
    source_title = serializers.CharField()

    content = serializers.CharField()
    like = serializers.IntegerField()
    dislike = serializers.IntegerField()
    is_recommend = serializers.IntegerField()
    reply_message = serializers.CharField(allow_null=True, allow_blank=True)

    created = serializers.DateTimeField()


class CommentListSerializer(BaseListSerializer):
    child = CommentDetailSerializer()
