# -*- coding:utf8 -*-
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.conf import settings

from horizon.models import model_to_dict
from horizon import main
from horizon.decorators import has_permission_to_update
from horizon.serializers import (BaseListSerializer,
                                 BaseModelSerializer,
                                 BaseSerializer,
                                 timezoneStringTostring)
from users.models import User, IdentifyingCode, Role, WXAuthorizedIdentifyingCode

from Admin_App.ad_coupons.models import CouponsSendRecord

import urllib
import os
import json
import re
import copy


class WXUserSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            _data = copy.deepcopy(data)
            _data['gender'] = _data.pop('sex')
            _data['wx_out_open_id'] = _data.pop('openid')
            # data['head_picture'] = data.pop('headimgurl')
            # _data['phone'] = 'WX%s' % main.make_random_char_and_number_of_string(18)
            self.make_correct_params(_data)
            super(WXUserSerializer, self).__init__(data=_data, **kwargs)
        else:
            super(WXUserSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = User
        fields = ('email', 'weibo', 'phone', 'wb_uid', 'wx_out_open_id',
                  'nickname', 'gender', 'province', 'city', 'head_picture')

    def is_valid(self, raise_exception=False):
        result = super(WXUserSerializer, self).is_valid(raise_exception)
        if not result:
            if self.errors.keys() == ['head_picture']:
                return True
            return False
        return True

    def save(self, **kwargs):
        kwargs['channel'] = 'WX'
        # kwargs['password'] = make_password(self.validated_data['wx_out_open_id'])
        kwargs['password'] = ''
        kwargs['head_picture'] = self.initial_data['headimgurl']
        return super(WXUserSerializer, self).save(**kwargs)

    def make_correct_params(self, source_dict):
        """
        解决微信授权登录后返回用户信息乱码的问题
        """
        zh_cn_list = ['nickname', 'city', 'province', 'country']
        compile_str = '\\u00[0-9a-z]{2}'
        re_com = re.compile(compile_str)
        for key in source_dict.keys():
            if key in zh_cn_list:
                utf8_list = re_com.findall(json.dumps(source_dict[key]))
                unicode_list = []
                for ch_item in utf8_list:
                    exec('unicode_list.append("\\x%s")' % ch_item.split('u00')[1])
                key_tmp_list = [json.dumps(source_dict[key])[1:-1]]
                for item2 in utf8_list:
                    tmp2 = key_tmp_list[-1].split('\\%s' % item2, 1)
                    key_tmp_list.pop(-1)
                    key_tmp_list.extend(tmp2)

                for index in range(len(key_tmp_list)):
                    if not key_tmp_list[index]:
                        if index < len(unicode_list):
                            key_tmp_list[index] = unicode_list[index]
                try:
                    source_dict[key] = ''.join(key_tmp_list).decode('utf8')
                except:
                    source_dict[key] = ''
        return source_dict


class WBUserSerializer(BaseModelSerializer):
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            _data = {'gender': data['gender'],
                     'wb_uid': data['uid'],
                     'nickname': data['screen_name'],
                     'province': data['province'],
                     'city': data['city'],
                     }
            #        'head_picture': data['avatar_large']
            # data['head_picture'] = data.pop('headimgurl')
            # _data['phone'] = 'WX%s' % main.make_random_char_and_number_of_string(18)
            # self.make_correct_params(_data)
            super(WBUserSerializer, self).__init__(data=_data, **kwargs)
        else:
            super(WBUserSerializer, self).__init__(instance, **kwargs)

    class Meta:
        model = User
        fields = ('email', 'weibo', 'phone', 'wb_uid', 'wx_out_open_id',
                  'nickname', 'gender', 'province', 'city', 'head_picture')

    def is_valid(self, raise_exception=False):
        result = super(WBUserSerializer, self).is_valid(raise_exception)
        if not result:
            if self.errors.keys() == ['head_picture']:
                return True
            return False
        return True

    def save(self, **kwargs):
        kwargs['channel'] = 'WB'
        # kwargs['password'] = make_password(self.validated_data['wb_uid'])
        kwargs['password'] = ''
        kwargs['head_picture'] = self.initial_data['avatar_large']
        return super(WBUserSerializer, self).save(**kwargs)


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ('id', 'phone', 'email', 'nickname', 'head_picture',)

    @has_permission_to_update
    def update_password(self, request, instance, validated_data):
        password = validated_data.get('password', None)
        if password is None:
            raise ValueError('Password is cannot be empty.')
        validated_data['password'] = make_password(password)
        return super(UserSerializer, self).update(instance, validated_data)

    @has_permission_to_update
    def update_userinfo(self, request, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).update(instance, validated_data)

    def binding_phone_or_email_to_user(self, request, instance, validated_data):
        if validated_data['username_type'] == 'phone':
            _validated_data = {'phone': validated_data['username']}
        else:
            _validated_data = {'email': validated_data['username']}
        return super(UserSerializer, self).update(instance, _validated_data)


class UserInstanceSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'email', 'nickname', 'head_picture',)


class UserDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    phone = serializers.CharField(allow_blank=True, allow_null=True)
    email = serializers.EmailField(allow_blank=True, allow_null=True)
    nickname = serializers.CharField(allow_blank=True, allow_null=True)
    role = serializers.CharField(allow_blank=True, allow_null=True)
    channel = serializers.CharField()

    wb_uid = serializers.IntegerField(allow_null=True)
    wx_out_open_id = serializers.IntegerField(allow_null=True)
    have_set_password = serializers.BooleanField()
    binding_wb = serializers.BooleanField()
    binding_wx = serializers.BooleanField()

    gender = serializers.IntegerField(allow_null=True)
    birthday = serializers.DateField(allow_null=True)
    province = serializers.CharField(allow_blank=True, allow_null=True)
    city = serializers.CharField(allow_blank=True, allow_null=True)

    last_login = serializers.DateTimeField()
    head_picture = serializers.ImageField()


class UserListSerializer(BaseListSerializer):
    child = UserDetailSerializer()


class IdentifyingCodeSerializer(BaseModelSerializer):
    class Meta:
        model = IdentifyingCode
        fields = '__all__'


class RoleDetailSerializer(BaseModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class RoleListSerializer(BaseListSerializer):
    child = RoleDetailSerializer()


class WXAuthorizedIdentifyingCodeSerializer(BaseModelSerializer):
    class Meta:
        model = WXAuthorizedIdentifyingCode
        fields = '__all__'


class WXAuthorizedIdentifyingCodeDetailSerializer(BaseSerializer):
    identifying_code = serializers.CharField()
    qrcode_url = serializers.CharField()

