# -*- coding:utf8 -*-
from django.db import models
from django.utils.timezone import now
from oauth2_provider.models import (Application as Oauth2_Application,
                                    AccessToken as Oauth2_AccessToken,
                                    RefreshToken as Oauth2_RefreshToken)

from horizon.main import minutes_15_plus, minutes_5_plus
from horizon.models import BaseTimeLimitManager, model_to_dict

from hashlib import md5
import datetime
import json


class WXAccessToken(models.Model):
    access_token = models.CharField(u'微信授权访问用户的token', max_length=164, unique=True)
    refresh_token = models.CharField(u'刷新access token的token', max_length=164, unique=True)
    openid = models.CharField(u'微信用户唯一标识', max_length=64, db_index=True)
    scope = models.CharField(u'用户授权的作用域', max_length=64)
    unionid = models.CharField(u'unionid', max_length=32, default='', null=True, blank=True)
    state = models.CharField(u'获取微信code的随机数', max_length=128)
    expires = models.DateTimeField(u'过期时间')

    class Meta:
        db_table = 'by_wxauth_accesstoken'
        ordering = ['-expires']

    def __unicode__(self):
        return self.openid

    @classmethod
    def get_object_by_openid(cls, openid):
        instances = cls.objects.filter(**{'openid': openid, 'expires__gt': now()})
        if instances:
            return instances[0]
        else:
            return None


class WXRandomString(models.Model):
    """
    微信授权登录随机码
    """
    random_str = models.CharField(u'随机字符串', max_length=32, db_index=True)
    status = models.IntegerField(u'随机字符串状态', default=0)     # 0：未使用，1：已使用
    expires = models.DateTimeField(u'过期时间', default=minutes_5_plus)
    access_token_data = models.CharField(u'微信授权登陆后获取的token信息(JSON字符串)',
                                         max_length=256, null=True, blank=True)

    objects = BaseTimeLimitManager()

    class Meta:
        db_table = 'by_wxauth_randomstring'
        ordering = ['-expires']

    def __unicode__(self):
        return self.random_str

    @property
    def perfect_data(self):
        detail = model_to_dict(self)
        try:
            detail['access_token_data'] = json.loads(detail['access_token_data'])
        except:
            pass
        return detail

    @classmethod
    def get_object_by_random_str(cls, random_str):
        # random_str = md5(random_str).hexdigest()
        instances = cls.objects.filter(**{'random_str': random_str,
                                          'expires__gt': now(),
                                          'status': 0})
        if instances:
            return instances[0]
        else:
            return None

    @classmethod
    def get_object(cls, **kwargs):
        try:
            instance = cls.objects.get(**kwargs)
        except Exception as e:
            return e
        return instance

    @classmethod
    def get_detail(cls, **kwargs):
        instance = cls.get_object(**kwargs)
        if isinstance(instance, Exception):
            return instance
        return instance.perfect_data


class WXAPPInformation(models.Model):
    app_id = models.CharField(u'开发者ID（APPID）', max_length=32)
    app_secret = models.CharField(u'开发者秘钥（APPSECRET）', max_length=64)
    created = models.DateTimeField(u'创建时间', default=now)

    class Meta:
        db_table = 'by_wx_app_information'

    def __unicode__(self):
        return self.app_id

    @classmethod
    def get_object(cls):
        try:
            return cls.objects.all()[0]
        except Exception as e:
            return e
