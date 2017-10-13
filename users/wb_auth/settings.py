# -*- coding:utf8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse

from users.wb_auth.models import WBAPPInformation
from horizon import main

import urllib
import os

# 微博授权第三方登录接口域名
WB_AUTH_API_URL = 'https://api.weibo.com/oauth2/'

# 微博获取用户信息URL
WB_AUTH_GET_USER_INFO_URL = 'https://api.weibo.com/2/users/show.json'

wb_app_info = WBAPPInformation.get_object()

# 公众账号ID
APPID = wb_app_info.app_id

# APP密钥
APPSECRET = wb_app_info.app_secret

# 应用授权作用域 （snsapi_userinfo代表：获取用户个人信息）
SCOPE = 'snsapi_userinfo'

# 授权类型
GRANT_TYPE = {
    'get_access_token': 'authorization_code',
    'refresh_token': 'refresh_token',
}

# 微博授权接口参数配置

# 微博授权登录回调地址 (前端页面)
if settings.ENVIRONMENT == 10:    # 开发环境
    REDIRECT_URI = 'http://yinshi.weixin.city23.com/login/wexincallback/?callback_url=%s'
elif settings.ENVIRONMENT == 20:  # 测试环境
    REDIRECT_URI = 'http://yinshi.weixin.city23.com/login/wexincallback/?callback_url=%s'
elif settings.ENVIRONMENT == 30:  # 生产环境
    REDIRECT_URI = 'http://yinshin.net/login/wexincallback/?callback_url=%s'
else:
    REDIRECT_URI = 'http://yinshi.weixin.city23.com/login/wexincallback/?callback_url=%s'

# 网页授权登录参数配置
WB_AUTH_PARAMS = {
    'get_code': {
        'client_id': APPID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        # 'scope': 'snsapi_userinfo',
        'state': main.make_random_char_and_number_of_string,
        # 'end_params': '#wechat_redirect',
    },
    'get_access_token': {
        'client_id': APPID,
        'client_secret': APPSECRET,
        'code': None,
        'grant_type': GRANT_TYPE['get_access_token'],
        'redirect_uri': REDIRECT_URI,
    },
    'refresh_token': {
        'client_id': APPID,
        'grant_type': GRANT_TYPE['refresh_token'],
        'refresh_token': None
    },
    'get_userinfo': {
        'uid': None,
        'access_token': None,
    }
}

# 微博授权登录url配置
WB_AUTH_URLS = {
    'get_code': os.path.join(WB_AUTH_API_URL, 'authorize'),
    'get_access_token': os.path.join(WB_AUTH_API_URL, 'access_token'),
    'refresh_token': os.path.join(WB_AUTH_API_URL, 'sns/oauth2/refresh_token'),
    'get_userinfo': WB_AUTH_GET_USER_INFO_URL,
}
