# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from horizon.views import APIView
from media.permissions import IsOwnerOrReadOnly
from media.models import (Media, ResourceTags,
                          ThemeType,
                          MediaType,
                          ProjectProgress,
                          Information,
                          Case, RESOURCE_COLUMN_CONFIG,
                          ResourceOpinionRecord,
                          AdvertResource)
from media.forms import (MediaTypeListForm,
                         ThemeTypeListForm,
                         ProgressListForm,
                         MediaListForm,
                         MediaDetailForm,
                         InformationDetailForm,
                         InformationListForm,
                         CaseDetailForm,
                         CaseListForm,
                         SourceLikeActionForm,
                         AdvertResourceListForm,
                         RelevantCaseForMediaForm,
                         RecommendMediaForm,
                         RelevantInformationListForm,
                         RelevantCaseListForm,
                         SearchResourceActionForm)
from media.serializers import (MediaTypeListSerailizer,
                               ThemeTypeListSerializer,
                               ProgressListSerializer,
                               MediaDetailSerializer,
                               MediaListSerializer,
                               InformationDetailSerializer,
                               InformationListSerializer,
                               CaseDetailSerializer,
                               CaseListSerializer,
                               AdvertResourceListSerializer,
                               ResourceListSerializer)
from comment.models import SOURCE_TYPE_DB
from media.caches import MediaCache, SourceModelAction

import re
import copy


class MediaTypeList(APIView):
    """
    资源类型列表
    """
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


class ThemeTypeList(APIView):
    """
    题材类别列表
    """
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


class ProgressList(APIView):
    """
    项目进度列表
    """
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


class MediaDetail(APIView):
    """
    媒体资源详情
    """
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

        # 增加浏览量
        SourceModelAction.update_read_count(source_type=1, source_id=cld['id'])
        return Response(serializer.data, status=status.HTTP_200_OK)


class MediaList(APIView):
    """
    媒体资源列表
    """
    def search_action(self, **search_kwargs):
        media_search_dict = MediaCache().get_media_search_dict()
        match_result = []
        for media_id, media_detail in media_search_dict.items():
            does_match = False
            for kw, value in search_kwargs.items():
                if media_detail.get(kw) != value:
                    break
            else:
                does_match = True
            if does_match:
                match_result.append({'media_id': media_id,
                                     'media_detail': media_detail})
        return match_result

    def get_media_detail_list(self, **kwargs):
        sort_key = kwargs['sort'] if kwargs.get('sort') else 'updated'
        pop_keys = ('sort', 'page_size', 'page_index')
        for key in pop_keys:
            if key in kwargs:
                kwargs.pop(key)

        match_media_list = self.search_action(**kwargs)
        match_media_list = sorted(match_media_list,
                                  key=lambda x: x['media_detail'][sort_key], reverse=True)

        perfect_details = []
        for item_media in match_media_list:
            media_detail = MediaCache().get_media_detail_by_id(item_media['media_id'])
            perfect_details.append(media_detail)
        return perfect_details

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


class InformationDetail(APIView):
    """
    资讯详情
    """
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


class InformationList(APIView):
    """
    资讯列表
    """
    def search_action(self, **search_kwargs):
        information_search_dict = MediaCache().get_information_search_dict()
        match_result = []
        for information_id, information_detail in information_search_dict.items():
            does_match = False
            for kw, value in search_kwargs.items():
                if information_detail.get(kw) != value:
                    break
            else:
                does_match = True
            if does_match:
                match_result.append({'information_id': information_id,
                                     'information_detail': information_detail})
        return match_result

    def get_information_detail_list(self, **kwargs):
        sort_key = kwargs['sort'] if 'sort' in kwargs else 'updated'
        # 最新发布（栏目）
        if kwargs.get('column') == RESOURCE_COLUMN_CONFIG['newest']:
            kwargs.pop('column')
        pop_keys = ('page_size', 'page_index')
        for key in pop_keys:
            if key in kwargs:
                kwargs.pop(key)

        match_information_list = self.search_action(**kwargs)
        match_information_list = sorted(
            match_information_list,
            key=lambda x: x['information_detail'][sort_key],
            reverse=True
        )

        perfect_details = []
        for item_media in match_information_list:
            detail = MediaCache().get_information_detail_by_id(item_media['information_id'])
            perfect_details.append(detail)
        return perfect_details

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


class CaseDetail(APIView):
    """
    案例详情
    """
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


class CaseList(APIView):
    """
    案例列表
    """
    def search_action(self, **search_kwargs):
        case_search_dict = MediaCache().get_case_search_dict()
        match_result = []
        for case_id, case_detail in case_search_dict.items():
            does_match = False
            for kw, value in search_kwargs.items():
                if case_detail.get(kw) != value:
                    break
            else:
                does_match = True
            if does_match:
                match_result.append({'case_id': case_id,
                                     'case_detail': case_detail})
        return match_result

    def get_case_detail_list(self, **kwargs):
        sort_key = kwargs['sort'] if 'sort' in kwargs else 'updated'
        # 最新发布（栏目）
        if kwargs.get('column') == RESOURCE_COLUMN_CONFIG['newest']:
            kwargs.pop('column')
        pop_keys = ('page_size', 'page_index')
        for key in pop_keys:
            if key in kwargs:
                kwargs.pop(key)

        match_case_list = self.search_action(**kwargs)
        match_case_list = sorted(match_case_list,
                                 key=lambda x: x['case_detail'][sort_key], reverse=True)

        perfect_details = []
        for item_case in match_case_list:
            detail = MediaCache().get_case_detail_by_id(item_case['case_id'])
            perfect_details.append(detail)
        return perfect_details

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
    """
    对资源点赞
    """
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


class AdvertResourceList(APIView):
    """
    广告资源列表
    """
    def get_advert_resource_list(self, source_type):
        return MediaCache().get_advert_list(source_type)

    def post(self, request, *args, **kwargs):
        form = AdvertResourceListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_advert_resource_list(cld['source_type'])
        if isinstance(instances, Exception):
            return Response({'Detail': instances.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AdvertResourceListSerializer(instances)
        list_data = serializer.list_data(**cld)
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)


# 根据提供的标签列表，匹配相关度最高的资源
def match_resource_action_with_tags(tags_dict, tags):
    import json
    if isinstance(tags, (str, unicode)):
        try:
            tags = json.loads(tags)
        except Exception as e:
            return e
    else:
        if not isinstance(tags, list):
            return Exception('Params tags is incorrect.')

    match_result = []
    for tags_key, item_ids in tags_dict.items():
        perfect_key = tags_key.split(':')
        match_count = 0
        for item2_key in tags:
            if str(item2_key) in perfect_key:
                match_count += 1
        match_result.append({'tags_key': tags_key,
                             'match_count': match_count})
    match_result = sorted(match_result, key=lambda x: x['match_count'], reverse=True)
    perfect_result = []
    for match_item in match_result:
        tags_key = match_item['tags_key']
        perfect_result.extend(tags_dict[tags_key])

    return perfect_result


class RelevantCaseForMedia(APIView):
    """
    资源相关案例
    """
    def get_relevant_case_list(self, media_id):
        media = MediaCache().get_media_by_id(media_id)
        if isinstance(media, Exception):
            return media

        case_tags_key_dict = MediaCache().get_case_tags_dict()
        match_result = match_resource_action_with_tags(case_tags_key_dict, media.tags)
        if isinstance(match_result, Exception):
            return match_result

        case_list = []
        match_count = 2
        count = 0
        for case_id in match_result:
            case = MediaCache().get_case_detail_by_id(case_id)
            if isinstance(case, Exception):
                continue
            case_list.append(case)
            count += 1
            if count >= match_count:
                break
        return case_list[:2]

    def post(self, request, *args, **kwargs):
        form = RelevantCaseForMediaForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_relevant_case_list(cld['media_id'])
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CaseListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        list_data = serializer.list_data()
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)


class RecommendMediaList(APIView):
    """
    推荐资源
    """
    def get_recommend_media_list(self, media_id):
        media = MediaCache().get_media_by_id(media_id)
        if isinstance(media, Exception):
            return media

        media_tags_key_dict = MediaCache().get_media_tags_dict()
        match_result = match_resource_action_with_tags(media_tags_key_dict, media.tags)
        if isinstance(match_result, Exception):
            return match_result

        media_list = []
        match_count = 2
        count = 0
        for item_media_id in match_result:
            if item_media_id == media_id:
                continue
            item_media = MediaCache().get_media_detail_by_id(item_media_id)
            if isinstance(item_media, Exception):
                continue
            media_list.append(item_media)
            count += 1
            if count >= match_count:
                break
        return media_list[:2]

    def post(self, request, *args, **kwargs):
        form = RecommendMediaForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_recommend_media_list(cld['media_id'])
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MediaListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        list_data = serializer.list_data()
        return Response(list_data, status=status.HTTP_200_OK)


class RelevantInformationList(APIView):
    """
    资讯：相关文章
    """
    def get_relevant_information_list(self, information_id, match_count=6):
        information = MediaCache().get_information_by_id(information_id)
        if isinstance(information, Exception):
            return information

        information_tags_key_dict = MediaCache().get_information_tags_dict()
        match_result = match_resource_action_with_tags(information_tags_key_dict, information.tags)
        if isinstance(match_result, Exception):
            return match_result

        information_list = []
        count = 0
        for item_information_id in match_result:
            if item_information_id == information_id:
                continue
            item_information = MediaCache().get_information_detail_by_id(item_information_id)
            if isinstance(item_information, Exception):
                continue
            information_list.append(item_information)
            count += 1
            if count >= match_count:
                break
        return information_list[:match_count]

    def post(self, request, *args, **kwargs):
        form = RelevantInformationListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        kwargs = {}
        if cld.get('page_size'):
            kwargs['match_count'] = cld['page_size']
        details = self.get_relevant_information_list(cld['information_id'], **kwargs)
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InformationListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        list_data = serializer.list_data(**cld)
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)


class RelevantCaseList(APIView):
    """
    案例：相关文章
    """
    def get_relevant_case_list(self, case_id, match_count=6):
        case = MediaCache().get_case_by_id(case_id)
        if isinstance(case, Exception):
            return case

        case_tags_key_dict = MediaCache().get_case_tags_dict()
        match_result = match_resource_action_with_tags(case_tags_key_dict, case.tags)
        if isinstance(match_result, Exception):
            return match_result

        case_list = []
        count = 0
        for item_case_id in match_result:
            if item_case_id == case_id:
                continue
            item_case = MediaCache().get_case_detail_by_id(item_case_id)
            if isinstance(item_case, Exception):
                continue
            case_list.append(item_case)
            count += 1
            if count >= match_count:
                break
        return case_list[:match_count]

    def post(self, request, *args, **kwargs):
        form = RelevantCaseListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        kwargs = {}
        if cld.get('page_size'):
            kwargs['match_count'] = cld['page_size']
        details = self.get_relevant_case_list(cld['case_id'], **kwargs)
        if isinstance(details, Exception):
            return Response({'Detail': details.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CaseListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        list_data = serializer.list_data(**cld)
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)


class InformationDetailForNext(APIView):
    """
    资讯：下一篇
    """
    def get_next_information_detail(self, information_id):
        sort_order_list = MediaCache().get_information_sort_order_list()
        try:
            index = sort_order_list.index(information_id)
        except Exception as e:
            return e
        if len(sort_order_list) <= index + 1:
            return None
        detail = MediaCache().get_information_detail_by_id(sort_order_list[index+1])
        return detail

    def post(self, request, *args, **kwargs):
        form = InformationDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        detail = self.get_next_information_detail(cld['id'])
        if isinstance(detail, Exception) or not detail:
            return Response({}, status=status.HTTP_200_OK)
        serializer = InformationDetailSerializer(data=detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CaseDetailForNext(APIView):
    """
    案例：下一篇
    """
    def get_next_case_detail(self, case_id):
        sort_order_list = MediaCache().get_case_sort_order_list()
        try:
            index = sort_order_list.index(case_id)
        except Exception as e:
            return e
        if len(sort_order_list) <= index + 1:
            return None
        detail = MediaCache().get_case_detail_by_id(sort_order_list[index+1])
        return detail

    def post(self, request, *args, **kwargs):
        form = CaseDetailForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        detail = self.get_next_case_detail(cld['id'])
        if isinstance(detail, Exception) or not detail:
            return Response({}, status=status.HTTP_200_OK)
        serializer = CaseDetailSerializer(data=detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SearchResourceAction(APIView):
    """
    搜索资源
    """
    search_dict_config = {
        Media: MediaCache().get_media_search_dict(),
        Information: MediaCache().get_information_search_dict(),
        Case: MediaCache().get_case_search_dict(),
    }
    resource_detail_config = {
        Media: MediaCache().get_media_detail_by_id,
        Information: MediaCache().get_information_detail_by_id,
        Case: MediaCache().get_case_detail_by_id,
    }

    def search_action(self, search_dict, keywords):
        if isinstance(keywords, (str, unicode)):
            keywords = keywords.split()
        match_result = []
        re_com_list = [re.compile(keyword) for keyword in keywords]
        for source_id in search_dict:
            count = 0
            for key2, value2 in search_dict[source_id].items():
                if key2 == 'tags':
                    value2 = ' '.join(value2)
                for re_com in re_com_list:
                    try:
                        count += len(re_com.findall(value2))
                    except:
                        continue
            if count > 0:
                item_result = {'resource_id': source_id,
                               'match_count': count}
                match_result.append(item_result)

        return sorted(match_result, key=lambda x: x['match_count'], reverse=True)

    def get_search_resource_list(self, source_type, keywords):
        model_class = SOURCE_TYPE_DB[source_type]
        search_dict = self.search_dict_config[model_class]
        match_result = self.search_action(search_dict, keywords)

        detail_function = self.resource_detail_config[model_class]
        perfect_result = []
        for item in match_result:
            resource_id = item['resource_id']
            detail = detail_function(resource_id)
            if model_class == Media:
                detail['picture'] = detail['picture_profile']
            perfect_result.append(detail)
        return perfect_result

    def post(self, request, *args, **kwargs):
        form = SearchResourceActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        details = self.get_search_resource_list(cld['source_type'], cld['keywords'])
        serializer = ResourceListSerializer(data=details)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        list_data = serializer.list_data()
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)

