# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from horizon.views import APIView
from dimensions.serializers import (DimensionListSerializer,
                                    TagListSerializer,
                                    MediaSerializer,
                                    MatchActionListSerializer)
from dimensions.permissions import IsOwnerOrReadOnly
from dimensions.models import (Dimension, Attribute, Tag,
                               TagConfigure, AdjustCoefficient)
from dimensions.forms import (DimensionListForm,
                              TagsListForm,
                              ResourceMatchActionForm)
from dimensions.caches import DimensionCache
from media.models import Media, MediaConfigure, MediaType
from media.serializers import MediaDetailSerializer


from horizon.main import select_random_element_from_array

import json


class DimensionList(APIView):
    """
    维度列表
    """
    def get_dimension_list(self):
        return DimensionCache().get_dimension_list()
        # return Dimension.filter_objects()

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


class TagList(APIView):
    """
    标签列表
    """
    def get_tags_list(self, **kwargs):
        instances = DimensionCache().get_tag_list_by_dimension_id(dimension_id=kwargs['dimension_id'])
        # instances = Tag.filter_objects_by_dimension_id(dimension_id=kwargs['dimension_id'])
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


class ResourceMatchAction(APIView):
    """
    资源匹配
    """
    def get_dimension_list(self):
        return DimensionCache().get_dimension_list()
        # return Dimension.filter_objects()

    def get_adjust_coefficient_value_by_name(self, name):
        # kwargs = {'name': name.lower()}
        instance = DimensionCache().get_adjust_coefficient_by_name(adjust_coefficient_name=name.lower())
        # instance = AdjustCoefficient.get_object(**kwargs)
        if isinstance(instance, Exception):
            return 1
        return instance.value

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
        error_message_for_tags_list = 'Params [tags_list] is incorrect.'
        for item in tags_list:
            if sorted(item.keys()) != sorted(item_keys):
                return False, error_message_for_tags_list
            if item['dimension_id'] not in tag_ids_dict:
                return False, error_message_for_tags_list
            if not item['is_default_tag']:
                for tag_id in item['tag_ids']:
                    if tag_id not in tag_ids_dict[item['dimension_id']]:
                        return False, error_message_for_tags_list

        # 判断资源类型是否正确
        media_type = kwargs.get('media_type')
        if media_type:
            media_type_ids = [media_type_instance.id
                              for media_type_instance in MediaType.filter_objects()]
            if media_type not in media_type_ids:
                return False, 'Params [media_type] is not incorrect.'
        return True, None

    def match_action(self, first_dimension_id, tags_list, media_type=None):
        dimension_dict = {}
        media_match_dict = {}
        # 查找属性ID
        for item in tags_list:
            if item['is_default_tag']:
                tags_list = DimensionCache().get_tag_list_by_dimension_id(item['dimension_id'])
                item['tag_ids'] = [tag.id for tag in tags_list]
                # dimension_dict[item['dimension_id']] = {}
                # continue

            tag_config_instances = TagConfigure.filter_objects(tag_id__in=item['tag_ids'])
            attribute_dict = {}
            for item2 in tag_config_instances:
                attr_dict = attribute_dict.get(item2.attribute_id, {})
                tag_config_list = attr_dict.get('tag_config', [])

                match_value = item2.match_value
                if item['is_default_tag']:
                    match_value = 3.0
                tag_config_list.append({'tag_id': item2.tag_id,
                                        'match_value': match_value})
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
        dimension_instances = self.get_dimension_list()
        dimension_ids = [ins.id for ins in dimension_instances]
        media_value_result = {}
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
            media_value_result[media_id] = media_compute_dict_item

        # 对计算结果进行"阿尔法"调整优化
        kwargs = {'id__in': media_value_result.keys()}
        if media_type:
            kwargs['media_type'] = media_type
        media_instances = Media.filter_objects(**kwargs)
        media_instances_dict = {ins.id: ins for ins in media_instances}
        media_sum_result = []
        for media_id, value_dict in media_value_result.items():
            if media_id not in media_instances_dict:
                continue
            sum_value = 0
            for key, value in value_dict.items():
                sum_value += value
            # 从数据中读取"阿尔法"值
            alpha = self.get_adjust_coefficient_value_by_name(name='alpha')
            total = (sum_value + media_instances_dict[media_id].temperature) * alpha
            media_sum_result.append(
                {'media_id': media_id,
                 'data': {'total': total,
                          'first_dimension_value': value_dict[first_dimension_id]}
                 })

        # 对计算结果进行"贝塔"调整优化
        media_result = []
        media_tmp = sorted(media_sum_result, key=lambda x: x['data']['total'], reverse=True)[:10]
        media_tmp = sorted(media_tmp,
                           key=lambda x: x['data']['first_dimension_value'], reverse=True)
        # 从数据中读取"贝塔"值
        beta = self.get_adjust_coefficient_value_by_name(name='beta')
        for tmp_item in media_tmp[:3]:
            tmp_item['data']['total'] = (tmp_item['data']['total'] * beta) / 78.75 * 100
        media_result = sorted(media_tmp, key=lambda x: x['data']['total'], reverse=True)[:3]

        return media_result

    def get_media_list(self, **kwargs):
        return Media.filter_details(**kwargs)

    def get_perfect_media_result(self, match_result, media_list):
        media_dict = {item['id']: item for item in media_list}
        perfect_result = []
        for item in match_result:
            serializer = MediaDetailSerializer(media_dict[item['media_id']])
            item_dict = {'match_degree': '%.2f' % item['data']['total'],
                         'data': serializer.data}
            perfect_result.append(item_dict)
        return perfect_result

    def post(self, request, *args, **kwargs):
        form = ResourceMatchActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(**cld)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        tags_list = json.loads(cld['tags_list'])
        match_result = self.match_action(cld['first_dimension_id'],
                                         tags_list,
                                         media_type=cld.get('media_type'))
        media_ids = [item['media_id'] for item in match_result]
        media_list = self.get_media_list(id__in=media_ids)
        media_result = self.get_perfect_media_result(match_result, media_list)

        serializer = MatchActionListSerializer(data=media_result)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        list_data = serializer.list_data()
        if isinstance(list_data, Exception):
            return Response(list_data.args, status=status.HTTP_400_BAD_REQUEST)
        return Response(list_data, status=status.HTTP_200_OK)
