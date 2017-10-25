# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from dimensions.serializers import (DimensionListSerializer,
                                    TagListSerializer)
from dimensions.permissions import IsOwnerOrReadOnly
from dimensions.models import (Dimension, Attribute, Tag, TagConfigure)
from dimensions.forms import (DimensionListForm,
                              TagsListForm)

from horizon.main import select_random_element_from_array


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
