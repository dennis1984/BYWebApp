# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from dimensions.serializers import (DimensionListSerializer,
                                    TagListSerializer)
from dimensions.permissions import IsOwnerOrReadOnly
from dimensions.models import (Dimension, Attribute, Tag, TagConfigure)
from dimensions.forms import (DimensionListForm,
                              TagsListForm,
                              ResourceMatchActionForm)
from horizon.main import select_random_element_from_array

import json


class DimensionList(generics.GenericAPIView):
    """
    维度列表
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_dimension_list(self):
        return Dimension.filter_objects()

    def post(self, request, *args, **kwargs):
        form = DimensionListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_dimension_list()
        if isinstance(instances, Exception):
            return Response({'Detail': instances.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DimensionListSerializer(instances)
        data_list = serializer.list_data(**cld)
        if isinstance(data_list, Exception):
            return Response({'Detail': data_list.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data_list, status=status.HTTP_200_OK)


class TagList(generics.GenericAPIView):
    """
    标签列表
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_tags_list(self, **kwargs):
        instances = Tag.filter_objects_by_dimension_id(dimension_id=kwargs['dimension_id'])
        # 随机取出一定数量的元素
        new_instances = select_random_element_from_array(list(instances), kwargs['count'])
        return new_instances

    def post(self, request, *args, **kwargs):
        form = TagsListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_tags_list(**cld)
        serializer = TagListSerializer(instances)
        list_data = serializer.list_data(**cld)
        if isinstance(list_data, Exception):
            return Response({'Detail': list_data.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)


class ResourceMatchAction(generics.GenericAPIView):
    """
    资源匹配
    """
    def get_dimension_list(self):
        return Dimension.filter_objects()

    def is_request_data_valid(self, **kwargs):
        dimension_instances = self.get_dimension_list()
        dimensions_dict = {ins.id: ins for ins in dimension_instances}

        if kwargs['first_dimension_id'] not in dimensions_dict:
            return False, 'Params "first_dimension_id" is incorrect.'
        try:
            tags_list = json.loads(kwargs['tags_list'])
        except Exception as e:
            return False, e.args

        tag_ids_dict = {}
        for dimension_id in dimensions_dict:
            item_tags = Tag.filter_objects_by_dimension_id(dimension_id)
            tag_ids_dict[dimension_id] = [ins.id for ins in item_tags]

        item_keys = ['tag_ids', 'dimension_id', 'is_default_tag']
        error_message_for_tags_list = 'Params "tags_list" is incorrect.'
        for item in tags_list:
            if sorted(item.keys()) != sorted(item_keys):
                return False, error_message_for_tags_list
            if item['dimension_id'] not in tag_ids_dict:
                return False, error_message_for_tags_list
            if not item['is_default_tag']:
                for tag_id in item['tag_ids']:
                    if tag_id not in tag_ids_dict[item['dimension_id']]:
                        return False, error_message_for_tags_list
        return True, None

    def match_action(self, first_dimension_id, tag_ids_dict):
        pass

    def post(self, request, *args, **kwargs):
        form = ResourceMatchActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(**cld)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)
