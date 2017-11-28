# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from comment.serializers import (CommentSerializer,
                                 CommentDetailSerializer,
                                 CommentListSerializer)
from comment.permissions import IsOwnerOrReadOnly
from comment.models import (Comment, SOURCE_TYPE_DB)
from comment.forms import (CommentInputForm,
                           CommentListForm,
                           CommentDetailForm,
                           CommentDeleteForm)

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

        serializer = CommentSerializer(request, data=cld)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

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
