# -*- coding:utf8 -*-
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from users import views as users_view
from users.wx_auth import views as wx_auth_views
from users.wb_auth import views as wb_auth_views
from oauth2_provider.views.base import TokenView

urlpatterns = [
    url(r'^send_identifying_code/$', users_view.IdentifyingCodeAction.as_view()),
    url(r'^verify_identifying_code/$', users_view.IdentifyingCodeVerify.as_view()),
    url(r'^send_identifying_code_with_login/$', users_view.IdentifyingCodeActionWithLogin.as_view()),

    url(r'^user_not_logged_action/$', users_view.UserNotLoggedAction.as_view()),
    url(r'^user_action/$', users_view.UserAction.as_view()),
    url(r'^user_detail/$', users_view.UserDetail.as_view()),

    url(r'^role_list/$', users_view.RoleList.as_view()),

    # 微信授权登录
    url(r'^wx_login/$', users_view.WXAuthAction.as_view()),
    # 微信授权登录后获取token
    url(r'^wxauth/token/$', wx_auth_views.AuthCallback.as_view()),
    # 微信授权登录获取随机码
    url(r'^wx_authorized_identifying_code/$', users_view.WXAuthorizedIdentifyingCodeDetail.as_view()),

    # 微博授权登录
    url(r'^wb_login/$', users_view.WBAuthAction.as_view()),
    # 微博授权登录后获取token
    url(r'^wbauth/token/$', wb_auth_views.AuthCallback.as_view()),

    # 绑定手机号、邮箱及微博等
    url(r'^binding_action/$', users_view.UserBindingAction.as_view()),

    url(r'^login/$', TokenView.as_view(), name='login'),
    url(r'^logout/$', users_view.AuthLogout.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


