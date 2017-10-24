# -*- coding: utf8 -*-
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from media.serializers import (MediaSerializer,
                               ResourceTagsListSerializer)
from media.permissions import IsOwnerOrReadOnly
from media.models import (Media, ResourceTags)
from media.forms import (CollectActionForm,
                         CollectDeleteForm,
                         ResourceTagsListForm)


class CollectAction(generics.GenericAPIView):
    """
    钱包相关功能
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_collect_detail(self, request, cld):
        kwargs = {'user_id': request.user.id}
        if cld.get('pk'):
            kwargs['pk'] = cld['pk']
        if cld.get('dishes_id'):
            kwargs['dishes_id'] = cld['dishes_id']
        return Media.get_object(**kwargs)

    def does_dishes_exist(self, dishes_id):
        return True

    def post(self, request, *args, **kwargs):
        """
        用户收藏商品
        """
        form = CollectActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        collect_obj = self.get_collect_detail(request, cld)
        if not isinstance(collect_obj, Exception):
            serializer = MediaSerializer(collect_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if not self.does_dishes_exist(cld['dishes_id']):
            return Response({'Detail': 'Dishes %s does not existed' % cld['dishes_id']},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = MediaSerializer(data=cld, request=request)
        if serializer.is_valid():
            result = serializer.save()
            if isinstance(result, Exception):
                return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        删除收藏的商品
        """
        form = CollectDeleteForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        collect_obj = self.get_collect_detail(request, cld)
        if isinstance(collect_obj, Exception):
            return Response({'Detail': collect_obj.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = MediaSerializer(collect_obj)
        result = serializer.delete(request, collect_obj)
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResourceTagsList(generics.GenericAPIView):
    """
    媒体资源标签列表
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_tags_list(self):
        return ResourceTags.filter_objects()

    def post(self, request, *args, **kwargs):
        form = ResourceTagsListForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        instances = self.get_tags_list()
        if isinstance(instances, Exception):
            return Response({'Detail': instances.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ResourceTagsListSerializer(instances)
        data_list = serializer.list_data(**cld)
        if isinstance(data_list, Exception):
            return Response({'Detail': data_list.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data_list, status=status.HTTP_200_OK)
