# -*- coding:utf8 -*-
from __future__ import unicode_literals
import json
import datetime

from django.conf import settings
from horizon import redis
from django.utils.timezone import now

from media.models import (Media,
                          MediaType,
                          ThemeType,
                          ProjectProgress,
                          ResourceTags,
                          Information,
                          Case,
                          ResourceOpinionRecord,
                          AdvertResource)
from comment.models import Comment, SOURCE_TYPE_DB
from collect.models import Collect

# 过期时间（单位：秒）
EXPIRES_24_HOURS = 24 * 60 * 60
EXPIRES_10_HOURS = 10 * 60 * 60

RELEVANT_COUNT_CONFIG = {
    'like': ResourceOpinionRecord.get_like_count,
    'comment': Comment.get_comment_count,
    'collection': Collect.get_collection_count,
    'read': None,
}
COUNT_COLUMN_LIST = ('read', 'like', 'collection', 'comment')
COUNT_COLUMN_KEY_DICT = {
    'read': 'read_count',
    'like': 'like',
    'collection': 'collection_count',
    'comment': 'comment_count',
}


class MediaCache(object):
    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_SETTINGS['host'],
                                    port=settings.REDIS_SETTINGS['port'],
                                    db=settings.REDIS_SETTINGS['db_set']['web'])
        self.handle = redis.Redis(connection_pool=pool)

    # def get_dimension_id_key(self, dimension_id):
    #     return 'dimension_id:%s' % dimension_id
    #
    # def get_attribute_id_key(self, attribute_id):
    #     return 'attribute_id:%s' % attribute_id
    #
    # def get_tag_id_key(self, tag_id):
    #     return 'tag_id:%s' % tag_id

    def get_media_instance_id_key(self, media_id):
        return 'media:instance:id:%s' % media_id

    def get_media_id_key(self, media_id):
        return 'media:id:%s' % media_id

    def get_media_type_id_key(self, media_type_id):
        return 'media_type:id:%s' % media_type_id

    def get_theme_type_id_key(self, theme_type_id):
        return 'theme_type:id:%s' % theme_type_id

    def get_progress_id_key(self, progress_id):
        return 'progress:id:%s' % progress_id

    def get_resource_tag_id_key(self, resource_tag_id):
        return 'resource_tag:id:%s' % resource_tag_id

    def get_information_instance_id_key(self, information_id):
        return 'information:instance:id:%s' % information_id

    def get_information_id_key(self, information_id):
        return 'information:id:%s' % information_id

    def get_case_instance_id_key(self, case_id):
        return 'case:instance:id:%s' % case_id

    def get_case_id_key(self, case_id):
        return 'case:id:%s' % case_id

    def get_case_tags_dict_key(self):
        return 'case_tags_dict:tags'

    def get_media_tags_dict_key(self):
        return 'media_tags_dict:tags'

    def get_information_tags_dict_key(self):
        return 'information_tags_dict:tags'

    def get_media_sort_order_list_key(self):
        return 'media_sort_order_list:updated'

    def get_information_sort_order_list_key(self):
        return 'information_sort_order_list:updated'

    def get_case_sort_order_list_key(self):
        return 'case_sort_order_list:updated'

    def get_media_search_dict_title_tags_key(self):
        return 'media_search_dict:title_tags'

    def get_information_search_dict_title_tags_key(self):
        return 'information_search_dict:title_tags'

    def get_case_search_dict_title_tags_key(self):
        return 'case_search_dict:title_tags'

    def get_media_relevant_count_id_key(self, media_id, column='read'):
        column_list = ('read', 'like', 'collection', 'comment')
        if column not in column_list:
            return None
        return 'media_%s_count:id:%s' % (column, media_id)

    def get_information_relevant_count_id_key(self, information_id, column='read'):
        column_list = ('read', 'like', 'collection', 'comment')
        if column not in column_list:
            return None
        return 'information_%s_count:id:%s' % (column, information_id)

    def get_case_relevant_count_id_key(self, case_id, column='read'):
        column_list = ('read', 'like', 'collection', 'comment')
        if column not in column_list:
            return None
        return 'case_%s_count:id:%s' % (column, case_id)

    def get_advert_list_source_type_key(self, source_type):
        return 'advert_list:source_type:%s' % source_type

    def get_advert_detail_id_key(self, advert_id):
        return 'advert_detail:id:%s' % advert_id

    def set_instance_to_cache(self, key, data):
        self.handle.set(key, data)
        self.handle.expire(key, EXPIRES_24_HOURS)

    def set_list_to_cache(self, key, *list_data):
        self.handle.delete(key)
        self.handle.rpush(key, *list_data)
        self.handle.expire(key, EXPIRES_24_HOURS)

    def get_instance_from_cache(self, key):
        return self.handle.get(key)

    def get_list_from_cache(self, key, start=0, end=-1):
        return self.handle.lrange(key, start, end)

    def get_perfect_data(self, key, model_function, **kwargs):
        data = self.get_instance_from_cache(key)
        if not data:
            data = model_function(**kwargs)
            if isinstance(data, Exception):
                return data
            self.set_instance_to_cache(key, data)
        return data

    def get_perfect_list_data(self, key, model_function, **kwargs):
        list_data = self.get_list_from_cache(key)
        if not list_data:
            list_data = model_function(**kwargs)
            if isinstance(list_data, Exception) or not list_data:
                return list_data
            self.set_list_to_cache(key, *list_data)
        return list_data

    def get_perfect_ids_list_data(self, key, model_function, detail_key_function, **kwargs):
        list_data = self.get_list_from_cache(key)
        if not list_data:
            list_data = model_function(**kwargs)
            if isinstance(list_data, Exception):
                return list_data

            # 把每条数据逐次添加都缓存中
            for item_data in list_data:
                detail_key = detail_key_function(item_data['id'])
                if not self.get_instance_from_cache(detail_key):
                    self.set_instance_to_cache(detail_key, item_data)
            # 生成列表
            perfect_list_data = [item['id'] for item in list_data]
            self.set_list_to_cache(key, *perfect_list_data)
            return perfect_list_data
        return list_data

    # # 获取维度model对象
    # def get_dimension_by_id(self, dimension_id):
    #     key = self.get_dimension_id_key(dimension_id)
    #     return self.get_base_instance_by_key(dimension_id, key, Dimension)
    #
    # # 获取属性model对象
    # def get_attribute_by_id(self, attribute_id):
    #     key = self.get_attribute_id_key(attribute_id)
    #     return self.get_base_instance_by_key(attribute_id, key, Attribute)
    #
    # # 获取标签model对象
    # def get_tag_by_id(self, tag_id):
    #     key = self.get_tag_id_key(tag_id)
    #     return self.get_base_instance_by_key(tag_id, key, Tag)

    # 获取媒体资源Model对象
    def get_media_by_id(self, media_id):
        key = self.get_media_instance_id_key(media_id)
        kwargs = {'pk': media_id}
        return self.get_perfect_data(key, Media.get_object, **kwargs)

    # 获取媒体资源detail
    def get_media_detail_by_id(self, media_id):
        key = self.get_media_id_key(media_id)
        kwargs = {'pk': media_id}

        detail = self.get_perfect_data(key, Media.get_detail, **kwargs)
        if isinstance(detail, Exception):
            return detail
        for column in COUNT_COLUMN_LIST:
            count = self.get_media_relevant_count(media_id, column=column)
            count_key = COUNT_COLUMN_KEY_DICT[column]
            detail[count_key] = count
        return detail

    # 获取媒体资源的标签为Key的列表
    def get_media_tags_dict(self):
        key = self.get_media_tags_dict_key()
        return self.get_perfect_data(key, Media.get_tags_key_dict)

    # 获取资源类型model对象
    def get_media_type_by_id(self, media_type_id):
        key = self.get_media_id_key(media_type_id)
        kwargs = {'pk': media_type_id}
        return self.get_perfect_data(key, MediaType.get_object, **kwargs)

    # 获取题材类别model对象
    def get_theme_type_by_id(self, theme_type_id):
        key = self.get_theme_type_id_key(theme_type_id)
        kwargs = {'pk': theme_type_id}
        return self.get_perfect_data(key, ThemeType.get_object, **kwargs)

    # 获取项目进度model对象
    def get_progress_by_id(self, progress_id):
        key = self.get_progress_id_key(progress_id)
        kwargs = {'pk': progress_id}
        return self.get_perfect_data(key, ProjectProgress.get_object, **kwargs)

    # 获取资源标签model对象
    def get_resource_tag_by_id(self, resource_tag_id):
        key = self.get_resource_tag_id_key(resource_tag_id)
        kwargs = {'pk': resource_tag_id}
        return self.get_perfect_data(key, ResourceTags.get_object, **kwargs)

    # 获取资讯Model对象
    def get_information_by_id(self, information_id):
        key = self.get_information_instance_id_key(information_id)
        kwargs = {'pk': information_id}
        return self.get_perfect_data(key, Information.get_object, **kwargs)

    # 获取资讯详情
    def get_information_detail_by_id(self, information_id):
        key = self.get_information_id_key(information_id)
        kwargs = {'pk': information_id}

        detail = self.get_perfect_data(key, Information.get_detail, **kwargs)
        if isinstance(detail, Exception):
            return detail
        for column in COUNT_COLUMN_LIST:
            count = self.get_information_relevant_count(information_id, column=column)
            count_key = COUNT_COLUMN_KEY_DICT[column]
            detail[count_key] = count
        return detail

    # 获取资讯的标签为Key的列表
    def get_information_tags_dict(self):
        key = self.get_information_tags_dict_key()
        return self.get_perfect_data(key, Information.get_tags_key_dict)

    # 获取案例Model对象
    def get_case_by_id(self, case_id):
        key = self.get_case_instance_id_key(case_id)
        kwargs = {'pk': case_id}
        return self.get_perfect_data(key, Case.get_object, **kwargs)

    # 获取案例详情
    def get_case_detail_by_id(self, case_id):
        key = self.get_case_id_key(case_id)
        kwargs = {'pk': case_id}

        detail = self.get_perfect_data(key, Case.get_detail, **kwargs)
        if isinstance(detail, Exception):
            return detail
        for column in COUNT_COLUMN_LIST:
            count = self.get_case_relevant_count(case_id, column=column)
            count_key = COUNT_COLUMN_KEY_DICT[column]
            detail[count_key] = count
        return detail

    # 获取案例的标签为Key的列表
    def get_case_tags_dict(self):
        key = self.get_case_tags_dict_key()
        return self.get_perfect_data(key, Case.get_tags_key_dict)

    # 获取媒体资源排序顺序列表
    def get_media_sort_order_list(self):
        key = self.get_media_sort_order_list_key()
        return self.get_perfect_data(key, Media.get_sort_order_list)

    # 获取媒体资源排序顺序列表
    def get_information_sort_order_list(self):
        key = self.get_information_sort_order_list_key()
        return self.get_perfect_data(key, Information.get_sort_order_list)

    # 获取媒体资源排序顺序列表
    def get_case_sort_order_list(self):
        key = self.get_case_sort_order_list_key()
        return self.get_perfect_data(key, Case.get_sort_order_list)

    # 获取媒体资源ID为Key，title和tags为Value的字典（搜索用）
    def get_media_search_dict(self):
        key = self.get_media_search_dict_title_tags_key()
        return self.get_perfect_data(key, Media.get_search_dict)

    # 获取资讯ID为Key，title和tags为Value的字典（搜索用）
    def get_information_search_dict(self):
        key = self.get_information_search_dict_title_tags_key()
        return self.get_perfect_data(key, Information.get_search_dict)

    # 获取案例ID为Key，title和tags为Value的字典（搜索用）
    def get_case_search_dict(self):
        key = self.get_case_search_dict_title_tags_key()
        return self.get_perfect_data(key, Case.get_search_dict)

    # 获取媒体资源相关数量
    def get_media_relevant_count(self, media_id, column='read'):
        column_list = ('read', 'like', 'collection', 'comment')
        if column not in column_list:
            return Exception('Params [column] is must in %s' % list(column_list))

        source_type = None
        for m_key, model_class in SOURCE_TYPE_DB.items():
            if model_class == Media:
                source_type = m_key
                break
        key = self.get_media_relevant_count_id_key(media_id, column)
        if column != 'read':
            kwargs = {'source_type': source_type, 'source_id': media_id}
            model_function = RELEVANT_COUNT_CONFIG[column]
            return self.get_perfect_data(key, model_function, **kwargs)
        else:
            kwargs = {'media_id': media_id, 'column': column}
            return self.get_perfect_data(key, Media.get_relevant_count, **kwargs)

    # 获取资讯相关数量
    def get_information_relevant_count(self, information_id, column='read'):
        column_list = ('read', 'like', 'collection', 'comment')
        if column not in column_list:
            return Exception('Params [column] is must in %s' % list(column_list))

        source_type = None
        for m_key, model_class in SOURCE_TYPE_DB.items():
            if model_class == Information:
                source_type = m_key
                break
        key = self.get_information_relevant_count_id_key(information_id, column)
        if column != 'read':
            kwargs = {'source_type': source_type, 'source_id': information_id}
            model_function = RELEVANT_COUNT_CONFIG[column]
            return self.get_perfect_data(key, model_function, **kwargs)
        else:
            kwargs = {'information_id': information_id, 'column': column}
            return self.get_perfect_data(key, Information.get_relevant_count, **kwargs)

    # 获取案例相关数量
    def get_case_relevant_count(self, case_id, column='read'):
        column_list = ('read', 'like', 'collection', 'comment')
        if column not in column_list:
            return Exception('Params [column] is must in %s' % list(column_list))

        source_type = None
        for m_key, model_class in SOURCE_TYPE_DB.items():
            if model_class == Case:
                source_type = m_key
                break
        key = self.get_case_relevant_count_id_key(case_id, column)
        if column != 'read':
            kwargs = {'source_type': source_type, 'source_id': case_id}
            model_function = RELEVANT_COUNT_CONFIG[column]
            return self.get_perfect_data(key, model_function, **kwargs)
        else:
            kwargs = {'case_id': case_id, 'column': column}
            return self.get_perfect_data(key, Case.get_relevant_count, **kwargs)

    # 媒体资源相关数量加、减操作
    def media_relevant_count_action(self, media_id, column='read', action='plus', amount=1):
        self.get_media_relevant_count(media_id, column=column)
        key = self.get_media_relevant_count_id_key(media_id, column)
        if action == 'plus':
            return self.handle.incr(key, amount)
        else:
            return self.handle.decr(key, amount)

    # 资讯相关数量加、减操作
    def information_relevant_count_action(self, information_id, column='read',
                                          action='plus', amount=1):
        self.get_information_relevant_count(information_id, column=column)
        key = self.get_information_relevant_count_id_key(information_id, column)
        if action == 'plus':
            return self.handle.incr(key, amount)
        else:
            return self.handle.decr(key, amount)

    # 案例相关数量加、减操作
    def case_relevant_count_action(self, case_id, column='read', action='plus', amount=1):
        self.get_case_relevant_count(case_id, column=column)
        key = self.get_case_relevant_count_id_key(case_id, column)
        if action == 'plus':
            return self.handle.incr(key, amount)
        else:
            return self.handle.decr(key, amount)

    # def base_relevant_count_action(self, source_type, source_id, column='read',
    #                                action='plus', amount=1):
    #     source_type_key_dict = {
    #         # 媒体资源
    #         1: {'init': self.get_media_relevant_count,
    #             'key': self.get_media_relevant_count_id_key},
    #         # 案例
    #         2: {'init': self.get_case_relevant_count,
    #             'key': self.get_case_relevant_count_id_key},
    #         # 资讯
    #         3: {'init': self.get_information_relevant_count,
    #             'key': self.get_information_relevant_count}
    #     }
    #     get_count_function = source_type_key_dict[source_type]['init']
    #     key_function = source_type_key_dict[source_type]['key']
    #
    #     # 获取相关数量
    #     get_count_function(source_id, column=column)
    #     key = key_function(source_id, column)
    #     if action == 'plus':
    #         return self.handle.incr(key, amount)
    #     else:
    #         return self.handle.decr(key, amount)

    # 获取广告列表
    def get_advert_list(self, source_type):
        key = self.get_advert_list_source_type_key(source_type)
        kwargs = {'source_type': source_type}
        ids_list = self.get_perfect_ids_list_data(key,
                                                  AdvertResource.filter_detail,
                                                  self.get_advert_detail_id_key,
                                                  **kwargs)
        return self.get_perfect_list_data_by_ids(ids_list, self.get_advert_detail_id_key)

    def get_perfect_list_data_by_ids(self, ids_list, key_function):
        perfect_list_data = []
        for item_id in ids_list:
            id_key = key_function(item_id)
            kwargs = {'id': item_id}
            detail = self.get_perfect_data(id_key, AdvertResource.get_detail, **kwargs)
            if isinstance(detail, Exception):
                continue
            perfect_list_data.append(detail)
        return perfect_list_data


SOURCE_TYPE_CACHE_FUNCTION = {
    1: MediaCache().media_relevant_count_action,          # 媒体资源
    2: MediaCache().case_relevant_count_action,           # 案例
    3: MediaCache().information_relevant_count_action,    # 资讯
}
SYNC_CACHE_TO_DB = {
    1: Media.update_relevant_count_action,          # 媒体资源
    2: Case.update_relevant_count_action,           # 案例
    3: Information.update_relevant_count_action,    # 资讯
}


class SourceModelAction(object):
    """
    资源点赞、增加浏览数等操作
    """
    @classmethod
    def update_read_count(cls, source_type, source_id):
        if source_type not in SOURCE_TYPE_CACHE_FUNCTION:
            return Exception('Params [resource_type] is incorrect.')

        action_function = SOURCE_TYPE_CACHE_FUNCTION[source_type]
        count = action_function(source_id, column='read', action='plus')
        if count % 50 == 0:
            # 通过缓存数据到数据库
            sync_function = SYNC_CACHE_TO_DB[source_type]
            sync_function(source_id, attr=COUNT_COLUMN_KEY_DICT['read'], amount=count)
        return count

    @classmethod
    def update_like_count(cls, source_type, source_id):
        if source_type not in SOURCE_TYPE_CACHE_FUNCTION:
            return Exception('Params [resource_type] is incorrect.')

        action_function = SOURCE_TYPE_CACHE_FUNCTION[source_type]
        return action_function(source_id, column='like', action='plus')

    @classmethod
    def update_collection_count(cls, source_type, source_id, method='plus'):
        if source_type not in SOURCE_TYPE_CACHE_FUNCTION:
            return Exception('Params [resource_type] is incorrect.')
        if method not in ['plus', 'reduce']:
            return Exception('Params [resource_type] is incorrect.')

        action_function = SOURCE_TYPE_CACHE_FUNCTION[source_type]
        if method == 'plus':
            return action_function(source_id, column='collection', action='plus')
        else:
            return action_function(source_id, column='collection', action='reduce')

    @classmethod
    def update_comment_count(cls, source_type, source_id, method='plus'):
        if source_type not in SOURCE_TYPE_CACHE_FUNCTION:
            return Exception('Params [resource_type] is incorrect.')
        if method not in ['plus', 'reduce']:
            return Exception('Params [resource_type] is incorrect.')

        action_function = SOURCE_TYPE_CACHE_FUNCTION[source_type]
        if method == 'plus':
            return action_function(source_id, column='collection', action='plus')
        else:
            return action_function(source_id, column='collection', action='reduce')

    @classmethod
    def create_like_record(cls, request, source_type, source_id):
        init_data = {'user_id': request.user.id,
                     'source_type': source_type,
                     'source_id': source_id}
        record = ResourceOpinionRecord(**init_data)
        try:
            record.save()
        except Exception as e:
            return e
        return record

    @classmethod
    def like_action(cls, request, source_type, source_id):
        record = cls.create_like_record(request, source_type, source_id)
        if isinstance(record, Exception):
            return record
        source_ins = cls.update_like_count(source_type, source_id)
        if isinstance(source_ins, Exception):
            return source_ins
        return record, source_ins

