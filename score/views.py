# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now

from score.serializers import (ScoreSerializer,
                               ScoreRecordListSerializer)
from score.permissions import IsOwnerOrReadOnly
from score.models import (Score, ScoreRecord)
from score.forms import (ScoreRecordListForm,)

import json


class ScoreDetail(generics.GenericAPIView):
    """
    用户积分详情
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_score_object(self, request):
        instance = Score.get_object(user_id=request.user.id)
        if isinstance(instance, Exception):
            init_dict = {'user_id': request.user.id,
                         'score': 0,
                         'created': now(),
                         'updated': now()}
            instance = Score(**init_dict)
        return instance

    def post(self, request, *args, **kwargs):
        """
        获取用户积分详情
        """
        instance = self.get_score_object(request)
        serializer = ScoreSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ScoreRecordList(generics.GenericAPIView):
    """
    用户积分记录
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_score_record_list(self, request):
        return ScoreRecord.filter_objects(user_id=request.user.id)

    def post(self, request, *args, **kwargs):
        form = ScoreRecordListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_score_record_list(request)
        serializer = ScoreRecordListSerializer(instances)
        data_list = serializer.list_data(**cld)
        if isinstance(data_list, Exception):
            return Response({'Detail': data_list.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data_list, status=status.HTTP_200_OK)
