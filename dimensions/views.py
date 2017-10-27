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
from media.models import Media, MediaConfigure
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

    def match_action(self, first_dimension_id, tags_list):
        dimension_dict = {}
        media_match_dict = {}
        # 查找属性ID
        for item in tags_list:
            if item['is_default_tag']:
                dimension_dict[item['dimension_id']] = {}
                continue

            tag_config_instances = TagConfigure.filter_objects(tag_id__in=item['tag_ids'])
            attribute_dict = {}
            for item2 in tag_config_instances:
                attr_dict = attribute_dict.get(item2.attribute_id, {})
                tag_config_list = attr_dict.get('tag_config', [])
                tag_config_list.append({'tag_id': item2.tag_id,
                                        'match_value': item2.match_value})
                attr_dict['tag_config'] = tag_config_list

                media_ids = attr_dict.get('media_ids', [])
                if not media_ids:
                    media_ins = MediaConfigure.filter_objects(dimension_id=item['dimension_id'],
                                                              attribute_id=item2.attribute_id)
                    media_ids = [item3.media_id for item3 in media_ins]
                    attr_dict['media_ids'] = media_ids
                attribute_dict[item2.attribute_id] = attr_dict
            dimension_dict[item['dimension_id']] = attribute_dict

        # 生成匹配数据
        for dimension_id, item_dict in dimension_dict.items():
            for attribute_id, attr_conf_item in item_dict.items():
                for media_id in attr_conf_item['media_ids']:
                    media_dict_item = media_match_dict.get(media_id, {})
                    media_dime_dict_item = media_dict_item.get(dimension_id, {})
                    match_value_list = [item2['match_value']
                                        for item2 in attr_conf_item['tag_config']]
                    media_dime_dict_item[attribute_id] = match_value_list
                    media_dict_item[dimension_id] = media_dime_dict_item
                    media_match_dict[media_id] = media_dict_item

        # 匹配计算
        dimension_instances = Dimension.filter_objects()
        dimension_ids = [ins.id for ins in dimension_instances]
        compute_result = {}
        for media_id, dime_dict_item in media_match_dict.items():
            media_compute_dict_item = {}
            for dime_id in dimension_ids:
                if dime_id in dime_dict_item:
                    dime_value = 0
                    for attr_id, values_list in dime_dict_item[dime_id].items():
                        values_list = sorted(values_list)
                        max_value = values_list[-1]
                        offset_value = 0
                        for item in values_list[:-1]:
                            offset_value += item
                        offset_value = offset_value / 10
                        attr_value = max_value + offset_value
                        if attr_value > 5:
                            attr_value = 5
                        dime_value += attr_value
                    dime_value = dime_value / (len(dime_dict_item[dime_id]))
                else:
                    dime_value = 3
                media_compute_dict_item[dime_id] = dime_value
            compute_result[media_id] = media_compute_dict_item

        # 对计算结果进行优化、排序

        return compute_result

    def post(self, request, *args, **kwargs):
        form = ResourceMatchActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(**cld)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        first_dimension_id = cld['first_dimension_id']
        tags_list = json.loads(cld['tags_list'])
        match_result = self.match_action(first_dimension_id, tags_list)

        return Response(status=status.HTTP_200_OK)
