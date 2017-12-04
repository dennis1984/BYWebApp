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
from reports.caches import ReportCache
from score.models import SCORE_ACTION_DICT, Score
from score.caches import ScoreAction

import json
import os


class ReportList(generics.GenericAPIView):
    """
    用户下载报告列表
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_reports_list(self, request):
        return ReportCache().get_report_download_record_by_user_id(request.user.id)

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

    def get_score_of_user(self, request):
        score = Score.get_object(user_id=request.user.id)
        if isinstance(score, Exception):
            return 0
        return score.score

    def score_action(self, request):
        """
        扣除积分并添加积分消耗记录
        """
        return ScoreAction.score_action(request, action='download')

    def post(self, request, *args, **kwargs):
        form = ReportFileDownloadForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        score_count = self.get_score_of_user(request)
        if score_count < SCORE_ACTION_DICT['download']['score']:
            return Response({'Detail': 'Score count is not enough.'}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_report_object(cld['media_id'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)

        # 扣除积分及添加积分记录
        result = self.score_action(request)
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)

        file_name = instance.report_file.name
        base_file_name = os.path.basename(file_name)
        response = StreamingHttpResponse(self.download_file(file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="%s"' % base_file_name.encode('utf8')
        return response
