# -*- coding: utf8 -*-
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from users.wb_auth.serializers import (AccessTokenSerializer,
                                       RandomStringSerializer,
                                       Oauth2AccessTokenSerializer,
                                       Oauth2RefreshTokenSerializer)
from users.wb_auth.models import (WBRandomString,
                                  Oauth2_Application,
                                  Oauth2_RefreshToken,
                                  Oauth2_AccessToken)
from users.wb_auth.forms import AuthCallbackForm
from users.wb_auth import settings as wb_auth_settings
from users.serializers import WBUserSerializer
from users.models import User
from horizon.views import APIView
from horizon.http_requests import send_http_request
from horizon.main import make_time_delta

from Admin_App.ad_coupons.models import CouponsConfig

from oauthlib.common import generate_token
from django.utils.timezone import now
import json


class AuthCallback(APIView):
    """
    微博用户授权后回调
    """
    def verify_random_str(self, cld):
        """
        return: true: WXRandomString instance
                false: Exception
        """
        instance = WBRandomString.get_object_by_random_str(cld['state'])
        if isinstance(instance, Exception):
            return Exception(('Error', 'The random string is not existed.'))
        return instance

    def get_user_by_uid(self, uid):
        kwargs = {'wb_uid': uid}
        return User.get_object(**kwargs)

    def mark_user_login(self, user):
        """
        标记用户已经登录
        """
        user.last_login = now()
        user.save()
        return user

    def post(self, request, *args, **kwargs):
        """
        接受微博跳转页面传过来的code票据
        """
        form = AuthCallbackForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        result = self.verify_random_str(cld)
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = RandomStringSerializer(result)
        try:
            serializer.update(result, {'status': 1})
        except:
            pass

        # 获取access token
        access_token_params = wb_auth_settings.WB_AUTH_PARAMS['get_access_token']
        access_token_params['code'] = cld['code']
        access_token_url = wb_auth_settings.WB_AUTH_URLS['get_access_token']
        result = send_http_request(access_token_url, access_token_params)
        if isinstance(result, Exception) or not getattr(result, 'text'):
            return Response({'Detail': result.args},
                            status=status.HTTP_400_BAD_REQUEST)

        # 存储token
        response_dict = json.loads(result.text)
        if 'access_token' not in response_dict:
            return Response({'Detail': 'Get access token failed'},
                            status=status.HTTP_400_BAD_REQUEST)
        response_dict['state'] = cld['state']
        serializer = AccessTokenSerializer(data=response_dict)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response({'Detail': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        # 获取微博userinfo
        userinfo_params = wb_auth_settings.WB_AUTH_PARAMS['get_userinfo']
        userinfo_params['uid'] = response_dict['uid']
        userinfo_params['access_token'] = response_dict['access_token']
        userinfo_url = wb_auth_settings.WB_AUTH_URLS['get_userinfo']
        result = send_http_request(userinfo_url, userinfo_params)
        if isinstance(result, Exception) or not getattr(result, 'text'):
            return Response({'Detail': result.args},
                            status=status.HTTP_400_BAD_REQUEST)

        # 存储数据到用户表
        userinfo_response_dict = json.loads(result.text)
        if 'id' not in userinfo_response_dict:
            return Response({'Detail': 'Get User Info failed'},
                            status=status.HTTP_400_BAD_REQUEST)

        # 检查用户是否存在
        _user = self.get_user_by_uid(userinfo_response_dict['id'])
        if isinstance(_user, Exception):       # 新用户
            serializer = WBUserSerializer(data=userinfo_response_dict)
            if not serializer.is_valid():
                return Response({'Detail': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            _user = serializer.save()
            # is_binding = False
        _token = Oauth2AccessToken().get_token(_user)
        if isinstance(_token, Exception):
            return Response({'Detail': _token.args},
                            status=status.HTTP_400_BAD_REQUEST)
        # _token.update(**{'is_binding': is_binding})

        # 标记用户已经登录
        self.mark_user_login(_user)

        return Response(_token, status=status.HTTP_200_OK)


class Oauth2AccessToken(object):
    def get_user(self, user_id):
        kwargs = {'pk': user_id}
        return User.get_object(**kwargs)

    @property
    def application(self):
        try:
            return Oauth2_Application.objects.filter()[0]
        except Exception as e:
            return e

    def mark_user_login(self, user):
        """
        标记用户已经登录
        """
        user.last_login = now()
        user.save()
        return user

    def get_token(self, user):
        token_dict = {"access_token": generate_token(),
                      "token_type": "Bearer",
                      "expires_in": settings.OAUTH2_PROVIDER['ACCESS_TOKEN_EXPIRE_SECONDS'],
                      "refresh_token": generate_token(),
                      "scope": ' '.join(settings.OAUTH2_PROVIDER['SCOPES'].keys()),
                      'wx_out_open_id': user.wx_out_open_id,
                      'wb_uid': user.wb_uid}
        if isinstance(self.application, Exception):
            return self.application

        access_token_data = {'token': token_dict['access_token'],
                             'expires': make_time_delta(seconds=token_dict['expires_in']),
                             'scope': token_dict['scope'],
                             'application': self.application,
                             'user': user}
        _access_token = Oauth2_AccessToken(**access_token_data)
        if not _access_token.is_valid():
            return ValueError('Access token is not valid')
        _access_token.save()
        refresh_token_data = {'token': token_dict['refresh_token'],
                              'access_token': _access_token,
                              'application': self.application,
                              'user': user}
        _refresh_token = Oauth2_RefreshToken(**refresh_token_data)
        _refresh_token.save()

        # 标记用户已经登录
        self.mark_user_login(user)
        return token_dict
