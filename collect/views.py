# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from collect.serializers import (CollectSerializer,
                                 CollectListSerializer,)
from collect.permissions import IsOwnerOrReadOnly
from collect.models import (Collect, SOURCE_TYPE_DB)
from collect.forms import (CollectActionForm,
                           CollectListForm,
                           CollectDeleteForm)


class CollectAction(generics.GenericAPIView):
    """
    钱包相关功能
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_collect_object(self, request, **kwargs):
        kwargs.update({'user_id': request.user.id})
        return Collect.get_object(**kwargs)

    def does_collect_exist(self, request, **kwargs):
        instance = self.get_collect_object(request, **kwargs)
        if isinstance(instance, Exception):
            return False
        return True

    def get_source_object(self, **kwargs):
        source_class = SOURCE_TYPE_DB.get(kwargs['source_type'])
        if not source_class:
            return Exception('Params is incorrect')
        return source_class.get_object(pk=kwargs['source_id'])

    def post(self, request, *args, **kwargs):
        """
        用户收藏商品
        """
        form = CollectActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        does_collect_exist = self.does_collect_exist(request, **cld)
        if does_collect_exist:
            return Response({'Detail': 'Can not repeat collection.'},
                            status=status.HTTP_400_BAD_REQUEST)

        source_ins = self.get_source_object(**cld)
        if isinstance(source_ins, Exception):
            return Response({'Detail': source_ins.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CollectSerializer(request, data=cld)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """
        删除收藏的商品
        """
        form = CollectDeleteForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        collect_obj = self.get_collect_object(request, **cld)
        if isinstance(collect_obj, Exception):
            return Response({'Detail': collect_obj.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CollectSerializer(collect_obj)
        try:
            serializer.delete(collect_obj)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectList(generics.GenericAPIView):
    """
    用户收藏列表
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_collects_list(self, request, source_type):
        kwargs = {'user_id': request.user.id}
        if source_type == 0:
            kwargs['source_type__in'] = SOURCE_TYPE_DB.keys()
        else:
            kwargs['source_type'] = source_type

        return Collect.filter_details(**kwargs)

    def post(self, request, *args, **kwargs):
        form = CollectListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        collects = self.get_collects_list(request, cld['source_type'])
        if isinstance(collects, Exception):
            return Response({'Detail': collects.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CollectListSerializer(data=collects)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        data_list = serializer.list_data(**cld)
        if isinstance(data_list, Exception):
            return Response({'Detail': data_list.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data_list, status=status.HTTP_200_OK)
