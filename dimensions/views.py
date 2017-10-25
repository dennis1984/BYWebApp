# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from dimensions.serializers import (DimensionListSerializer,)
from dimensions.permissions import IsOwnerOrReadOnly
from dimensions.models import (Dimension, Attribute, Tag, TagConfigure)
from dimensions.forms import (DimensionListForm,)


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
