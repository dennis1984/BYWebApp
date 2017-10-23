# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from reports.serializers import (CommentSerializer,
                                 ReportDetailSerializer,
                                 ReportListSerializer)
from reports.permissions import IsOwnerOrReadOnly
from reports.models import (Report, ReportDownloadRecord)
from reports.forms import (CommentInputForm,
                           ReportListForm,
                           CommentDetailForm)

import json


class ReportList(generics.GenericAPIView):
    """
    用户下载报告列表
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_reports_list(self, request):
        return ReportDownloadRecord.filter_details(user_id=request.user.id)

    def post(self, request, *args, **kwargs):
        form = ReportListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        reports = self.get_reports_list(request)
        if isinstance(reports, Exception):
            return Response({'Detail': reports.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReportListSerializer(data=reports)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        data_list = serializer.list_data(**cld)
        if isinstance(data_list, Exception):
            return Response({'Detail': data_list.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data_list, status=status.HTTP_200_OK)


# class CommentDetail(generics.GenericAPIView):
#     """
#     点评详情
#     """
#     def get_comment_detail(self, request, orders_id):
#         kwargs = {'user_id': request.user.id,
#                   'orders_id': orders_id}
#         return Comment.get_comment_detail(**kwargs)
#
#     def post(self, request, *args, **kwargs):
#         form = CommentDetailForm(request.data)
#         if not form.is_valid():
#             return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)
#
#         cld = form.cleaned_data
#         detail = self.get_comment_detail(request, cld['orders_id'])
#         if isinstance(detail, Exception):
#             return Response({'Detail': detail.args}, status=status.HTTP_400_BAD_REQUEST)
#         serializer = CommentDetailSerializer(data=detail)
#         if not serializer.is_valid():
#             return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.data, status=status.HTTP_200_OK)
