# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from media.permissions import IsOwnerOrReadOnly
from media.models import (Media, ResourceTags,
                          ThemeType,
                          MediaType,
                          ProjectProgress)
from media.forms import (MediaTypeListForm,
                         ThemeTypeListForm,
                         ProgressListForm,
                         MediaListForm,
                         MediaDetailForm)
from media.serializers import (MediaTypeListSerailizer,
                               ThemeTypeListSerializer,
                               ProgressListSerializer,
                               MediaDetailSerializer,
                               MediaListSerializer,)


class MediaTypeList(generics.GenericAPIView):
    """
    资源类型列表
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_media_type_list(self, **kwargs):
        return MediaType.filter_objects(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        获取资源类型列表
        """
        form = MediaTypeListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_media_type_list()
        if isinstance(instances, Exception):
            return Response({'Detail': instances.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MediaTypeListSerailizer(instances)
        list_data = serializer.list_data(**cld)
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)


class ThemeTypeList(generics.GenericAPIView):
    """
    题材类别列表
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_theme_type_list (self, **kwargs):
        return ThemeType.filter_objects(**kwargs)

    def post(self, request, *args, **kwargs):
        form = ThemeTypeListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_theme_type_list()
        if isinstance(instances, Exception):
            return Response({'Detail': instances.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ThemeTypeListSerializer(instances)
        data_list = serializer.list_data(**cld)
        if isinstance(data_list, Exception):
            return Response({'Detail': data_list.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data_list, status=status.HTTP_200_OK)


class ProgressList(generics.GenericAPIView):
    """
    项目进度列表
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_progress_list(self, **kwargs):
        return ProjectProgress.filter_objects(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        获取项目进度列表
        """
        form = ProgressListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_progress_list()
        if isinstance(instances, Exception):
            return Response({'Detail': instances.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ProgressListSerializer(instances)
        data_list = serializer.list_data(**cld)
        if isinstance(data_list, Exception):
            return Response({'Detail': data_list.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data_list, status=status.HTTP_200_OK)


class MediaDetail(generics.GenericAPIView):
    """
    媒体资源详情
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_media_detail(self, media_id):
        return Media.get_detail(pk=media_id)

    def post(self, request, *args, **kwargs):
        """
        获取详情
        """
        form = MediaDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        detail = self.get_media_detail(cld['id'])
        if isinstance(detail, Exception):
            return Response({'Detail': detail.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MediaDetailSerializer(data=detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.data}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MediaList(generics.GenericAPIView):
    """
    媒体资源列表
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_media_detail_list(self, **kwargs):
        if 'media_type_id' in kwargs:
            kwargs['media_type'] = kwargs.pop('media_type_id')
        if 'theme_type_id' in kwargs:
            kwargs['theme_type'] = kwargs.pop('theme_type_id')
        if 'progress_id' in kwargs:
            kwargs['progress'] = kwargs.pop('progress_id')
        return Media.filter_details(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        获取列表
        """
        form = MediaListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_media_detail_list(**cld)
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MediaListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.data}, status=status.HTTP_400_BAD_REQUEST)
        list_data = serializer.list_data(**cld)
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)
