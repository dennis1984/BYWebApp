# -*- coding:utf8 -*-
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from django.conf import settings
from oauth2_provider.models import AccessToken
from horizon.models import (model_to_dict,
                            get_perfect_filter_params,
                            BaseManager)
from horizon.main import minutes_15_plus
import datetime
import re
import os


class UserManager(BaseUserManager):
    def create_user(self, username_type, username,  password, **kwargs):
        """
        创建用户，
        参数包括：username （手机号）
                 password （长度必须不小于6位）
        """
        if not username:
            raise ValueError('Username cannot be null!')
        if len(password) < 6:
            raise ValueError('Password length must not less then 6!')

        if username_type == 'phone':
            user = self.model(phone=username)
        elif username_type == 'email':
            user = self.model(email=username)
        else:
            raise ValueError('Param "username_type" is invalid.')

        # user = self.model(phone=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **kwargs):
        user = self.create_user(username_type='phone',
                                username=username,
                                password=password,
                                **kwargs)
        user.is_admin = True
        user.save(using=self._db)
        return user


HEAD_PICTURE_PATH = settings.PICTURE_DIRS['web']['head_picture']


class User(AbstractBaseUser):
    email = models.EmailField(u'邮箱', max_length=200, unique=True, db_index=True,
                              null=True, blank=True)
    phone = models.CharField(u'手机号', max_length=20, unique=True, db_index=True,
                             null=True, blank=True)
    wx_out_open_id = models.CharField(u'微信第三方唯一标识', max_length=64, unique=True,
                                      db_index=True, null=True, blank=True)
    wb_uid = models.CharField(u'微博uid', max_length=16, unique=True, db_index=True,
                              null=True, blank=True)
    nickname = models.CharField(u'昵称', max_length=100, null=True, blank=True)

    # 角色
    role = models.CharField(u'我的角色', max_length=32, null=True, blank=True)

    # 性别，0：未设定，1：男，2：女
    gender = models.IntegerField(u'性别', default=0)
    birthday = models.DateField(u'生日', null=True)
    province = models.CharField(u'所在省份或直辖市', max_length=16, null=True, blank=True)
    city = models.CharField(u'所在城市', max_length=32, null=True, blank=True)
    head_picture = models.ImageField(u'头像', max_length=200,
                                     upload_to=HEAD_PICTURE_PATH,
                                     default=os.path.join(HEAD_PICTURE_PATH, 'noImage.png'))

    # 注册渠道：客户端：WEB，微信第三方：WX，QQ第三方：QQ，淘宝：TB
    #         新浪微博：WB
    channel = models.CharField(u'注册渠道', max_length=20, default='WEB')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(u'创建时间', default=now)
    updated = models.DateTimeField(u'最后更新时间', auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['channel']

    class Meta:
        db_table = 'by_auth_user'
        # unique_together = ('nickname', 'food_court_id')

    def __unicode__(self):
        return self.phone

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def is_binding(self, username_type):
        # re_com = re.compile(r'^1[0-9]{10}$')
        # try:
        #     result = re_com.match('%s' % self.phone)
        # except:
        #     return False
        # if result is None:
        #     return False
        # return True
        if username_type == 'phone':
            if self.phone:
                return True
        elif username_type == 'email':
            if self.email:
                return True
        return False

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def get_object_by_username(cls, username_type, username):
        if username_type == 'phone':
            return cls.get_object(phone=username)
        elif username_type == 'email':
            return cls.get_object(email=username)
        else:
            return Exception('Params is incorrect.')

    @classmethod
    def get_user_detail(cls, request):
        """
        return: ConsumerUser instance
        """
        try:
            return cls.objects.get(pk=request.user.id)
        except Exception as e:
            return e

    @classmethod
    def get_objects_list(cls, request, **kwargs):
        """
        获取用户列表
        权限控制：只有管理员可以访问这些数据
        """
        if not request.user.is_admin:
            return Exception('Permission denied, Cannot access the method')

        _kwargs = {}
        if 'start_created' in kwargs:
            _kwargs['created__gte'] = kwargs['start_created']
        if 'end_created' in kwargs:
            _kwargs['created__lte'] = kwargs['end_created']
        _kwargs['is_admin'] = False
        try:
            return cls.objects.filter(**_kwargs)
        except Exception as e:
            return e


def make_token_expire(request):
    """
    置token过期
    """
    header = request.META
    token = header['HTTP_AUTHORIZATION'].split()[1]
    try:
        _instance = AccessToken.objects.get(token=token)
        _instance.expires = now()
        _instance.save()
    except:
        pass
    return True


class IdentifyingCode(models.Model):
    phone_or_email = models.CharField(u'手机号/邮箱', max_length=200, db_index=True)
    identifying_code = models.CharField(u'验证码', max_length=6)
    expires = models.DateTimeField(u'过期时间', default=minutes_15_plus)

    class Meta:
        db_table = 'by_identifying_code'
        ordering = ['-expires']

    def __unicode__(self):
        return self.phone_or_email

    @classmethod
    def get_object_by_phone_or_email(cls, username):
        instances = cls.objects.filter(**{'phone_or_email': username,
                                          'expires__gt': now()})
        if instances:
            return instances[0]
        else:
            return None


class Role(models.Model):
    """
    用户角色
    """
    name = models.CharField('角色名称', max_length=32)
    created = models.DateTimeField('创建时间')

    class Meta:
        db_table = 'by_user_role'

    def __unicode__(self):
        return self.name

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e
