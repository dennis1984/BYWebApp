# -*- coding:utf8 -*-
from rest_framework import serializers

from comment.models import Comment, CommentOpinionRecord
from comment.caches import CommentCache
from media.caches import SourceModelAction

from horizon.decorators import has_permission_to_update
from horizon.serializers import (BaseSerializer,
                                 BaseModelSerializer,
                                 BaseListSerializer)
from horizon.main import make_random_number_of_string
from horizon.decorators import has_permission_to_update

import json
import os


class CommentSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, request=None, **kwargs):
        if data:
            data['user_id'] = request.user.id
            super(CommentSerializer, self).__init__(data=data, **kwargs)
        else:
            super(CommentSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = Comment
        fields = '__all__'

    def save(self, **kwargs):
        instance = super(CommentSerializer, self).save(**kwargs)
        if isinstance(instance, Exception):
            return instance

        # 增加资源的评论数量
        SourceModelAction.update_comment_count(self.data['source_type'], self.data['source_id'])
        # 添加评论数据到评论列表中
        CommentCache().add_comment_to_user_comment_list(self.data['user_id'], instance.id)
        CommentCache().add_comment_to_source_comment_list(source_type=self.data['source_type'],
                                                          source_id=self.data['source_id'],
                                                          comment_id=instance.id)
        return instance

    def delete(self, instance):
        # 减少资源的评论数量
        SourceModelAction.update_comment_count(instance.source_type,
                                               instance.source_id,
                                               method='reduce')
        # 添加评论数据到评论列表中
        CommentCache().delete_comment_from_user_comment_list(instance.user_id, instance.id)
        CommentCache().delete_comment_form_source_comment_list(source_type=instance.source_type,
                                                               source_id=instance.source_id,
                                                               comment_id=instance.id)

        validated_data = {'status': instance.id + 1}

        return super(CommentSerializer, self).update(instance, validated_data)


class CommentDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    user_nickname = serializers.CharField(allow_blank=True, allow_null=True)
    user_head_picture = serializers.ImageField(allow_null=True)
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


class CommentOpinionRecordSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, request=None, **kwargs):
        if data:
            data['user_id'] = request.user.id
            super(CommentOpinionRecordSerializer, self).__init__(data=data, **kwargs)
        else:
            super(CommentOpinionRecordSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = CommentOpinionRecord
        fields = '__all__'
