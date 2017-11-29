# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from comment.serializers import (CommentSerializer,
                                 CommentDetailSerializer,
                                 CommentListSerializer,
                                 CommentOpinionRecordSerializer)
from comment.permissions import IsOwnerOrReadOnly
from comment.models import (Comment,
                            SOURCE_TYPE_DB,
                            CommentOpinionRecord,
                            CommentOpinionModelAction)
from comment.forms import (CommentInputForm,
                           CommentListForm,
                           CommentDetailForm,
                           CommentDeleteForm,
                           CommentForResourceListForm,
                           CommentOpinionActionForm)
from score.models import ScoreAction

import json


class CommentAction(generics.GenericAPIView):
    """
    点评相关功能
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def is_request_data_valid(self, request, **kwargs):
        instance = SOURCE_TYPE_DB[kwargs['source_type']].get_object(pk=kwargs['source_id'])
        if isinstance(instance, Exception):
            return False, 'The source of %s does not exist.' % kwargs['source_id']

        instance = Comment.get_object(user_id=request.user.id, **kwargs)
        if isinstance(instance, Comment):
            return False, 'Can not repeat commenting.'
        return True, None

    def get_comment_object(self, request, comment_id):
        return Comment.get_object(pk=comment_id, user_id=request.user.id)

    def score_action(self, request):
        """
        增加积分及添加积分记录
        """
        return ScoreAction.score_action(request, action='comment')

    def post(self, request, *args, **kwargs):
        """
        用户点评资源（资源、案例及资讯）
        """
        form = CommentInputForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(request, **cld)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CommentSerializer(data=cld, request=request)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        result = self.score_action(request)
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """
        删除评论
        """
        form = CommentDeleteForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_comment_object(request, cld['id'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CommentSerializer(instance)
        try:
            serializer.delete(instance)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentList(generics.GenericAPIView):
    """
    用户点评列表
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_comment_detail_list(self, request):
        return Comment.filter_details(user_id=request.user.id)

    def post(self, request, *args, **kwargs):
        form = CommentListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_comment_detail_list(request)
        serializer = CommentListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        data_list = serializer.list_data(**cld)
        if isinstance(data_list, Exception):
            return Response({'Detail': data_list.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data_list, status=status.HTTP_200_OK)


class CommentDetail(generics.GenericAPIView):
    """
    点评详情
    """
    def get_comment_detail(self, request, comment_id):
        kwargs = {'user_id': request.user.id,
                  'id': comment_id}
        return Comment.get_object(**kwargs)

    def post(self, request, *args, **kwargs):
        form = CommentDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        detail = self.get_comment_detail(request, cld['id'])
        if isinstance(detail, Exception):
            return Response({'Detail': detail.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CommentDetailSerializer(data=detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentForResourceList(generics.GenericAPIView):
    """
    获取媒体资源的用户评论列表
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_comment_list(self, source_type, source_id):
        kwargs = {'source_type': source_type,
                  'source_id': source_id}
        return Comment.filter_details(**kwargs)

    def post(self, request, *args, **kwargs):
        form = CommentForResourceListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        comment_list = self.get_comment_list(cld['source_type'], cld['source_id'])
        serializer = CommentListSerializer(data=comment_list)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        list_data = serializer.list_data(**cld)
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)


class CommentOpinionAction(generics.GenericAPIView):
    """
    用户对评论的评价（点赞、踩）
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_comment_opinion_record(self, request, comment_id):
        kwargs = {'user_id': request.user.id,
                  'comment_id': comment_id}
        return CommentOpinionRecord.get_object(**kwargs)

    def post(self, request, *args, **kwargs):
        form = CommentOpinionActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        record = self.get_comment_opinion_record(request, cld['comment_id'])
        if not isinstance(record, Exception):
            return Response({'Detail': 'Can not repeat operate.'}, status=status.HTTP_400_BAD_REQUEST)

        result = CommentOpinionModelAction.comment_opinion_action(request,
                                                                  comment_id=cld['comment_id'],
                                                                  action=cld['action'])
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Result': True}, status=status.HTTP_201_CREATED)

