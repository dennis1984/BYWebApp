# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from media.permissions import IsOwnerOrReadOnly
from media.models import (Media, ResourceTags,
                          ThemeType,
                          MediaType,
                          ProjectProgress,
                          Information,
                          Case,
                          ResourceOpinionRecord,
                          SourceModelAction,)
from media.forms import (MediaTypeListForm,
                         ThemeTypeListForm,
                         ProgressListForm,
                         MediaListForm,
                         MediaDetailForm,
                         InformationDetailForm,
                         InformationListForm,
                         CaseDetailForm,
                         CaseListForm,
                         SourceLikeActionForm)
from media.serializers import (MediaTypeListSerailizer,
                               ThemeTypeListSerializer,
                               ProgressListSerializer,
                               MediaDetailSerializer,
                               MediaListSerializer,
                               InformationDetailSerializer,
                               InformationListSerializer,
                               CaseDetailSerializer,
                               CaseListSerializer)
from media.caches import MediaCache


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
        return MediaCache().get_media_detail_by_id(media_id)

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
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        list_data = serializer.list_data(**cld)
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)


class InformationDetail(generics.GenericAPIView):
    """
    资讯详情
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_information_detail(self, information_id):
        return MediaCache().get_information_detail_by_id(information_id)

    def post(self, request, *args, **kwargs):
        """
        获取详情
        """
        form = InformationDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        detail = self.get_information_detail(cld['id'])
        if isinstance(detail, Exception):
            return Response({'Detail': detail.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InformationDetailSerializer(data=detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # 增加浏览量
        SourceModelAction.update_read_count(source_type=3, source_id=cld['id'])
        return Response(serializer.data, status=status.HTTP_200_OK)


class InformationList(generics.GenericAPIView):
    """
    资讯列表
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_information_detail_list(self, **kwargs):
        return Information.filter_details(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        获取列表
        """
        form = InformationListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_information_detail_list(**cld)
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InformationListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        list_data = serializer.list_data(**cld)
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)


class CaseDetail(generics.GenericAPIView):
    """
    案例详情
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_case_detail(self, case_id):
        return MediaCache().get_case_detail_by_id(case_id)

    def post(self, request, *args, **kwargs):
        """
        获取详情
        """
        form = CaseDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        detail = self.get_case_detail(cld['id'])
        if isinstance(detail, Exception):
            return Response({'Detail': detail.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CaseDetailSerializer(data=detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # 增加浏览量
        SourceModelAction.update_read_count(source_type=2, source_id=cld['id'])
        return Response(serializer.data, status=status.HTTP_200_OK)


class CaseList(generics.GenericAPIView):
    """
    案例列表
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_case_detail_list(self, **kwargs):
        return Case.filter_details(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        获取列表
        """
        form = CaseListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_case_detail_list(**cld)
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CaseListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        list_data = serializer.list_data(**cld)
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)


class SourceLikeAction(generics.GenericAPIView):
    permission_classes = (IsOwnerOrReadOnly,)

    def get_source_like_record(self, request, source_type, source_id):
        kwargs = {'user_id': request.user.id,
                  'source_type': source_type,
                  'source_id': source_id}
        return ResourceOpinionRecord.get_object(**kwargs)

    def post(self, request, *args, **kwargs):
        form = SourceLikeActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        record = self.get_source_like_record(request, cld['source_type'], cld['source_id'])
        if not isinstance(record, Exception):
            return Response({'Detail': 'Can not repeat operate this action'},
                            status=status.HTTP_400_BAD_REQUEST)

        result = SourceModelAction.like_action(request, cld['source_type'], cld['source_id'])
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Result': True}, status=status.HTTP_201_CREATED)

