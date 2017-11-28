# -*- coding: utf8 -*-
from django.http import StreamingHttpResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from reports.serializers import (ReportListSerializer,)
from reports.permissions import IsOwnerOrReadOnly
from reports.models import (Report, ReportDownloadRecord)
from reports.forms import (ReportListForm,
                           ReportFileDownloadForm)

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


class ReportFileDownload(generics.GenericAPIView):
    """
    媒体资源报告文件下载
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_report_object(self, media_id):
        return Report.get_object(media_id=media_id)

    def download_file(self, file_name, buffer_size=512):
        with open(file_name) as fp:
            while True:
                text = fp.read(buffer_size)
                if text:
                    yield text
                else:
                    break

    def post(self, request, *args, **kwargs):
        form = ReportFileDownloadForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instance = self.get_report_object(cld['media_id'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)

        file_name = instance.report_file.name
        response = StreamingHttpResponse(self.download_file(file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename=%s' % file_name
        return response
