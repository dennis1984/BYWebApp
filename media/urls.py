# -*- coding:utf8 -*-
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from media import views

urlpatterns = [
    url(r'^media_type_list/$', views.MediaTypeList.as_view()),
    url(r'^theme_type_list/$', views.ThemeTypeList.as_view()),
    url(r'^progress_list/$', views.ProgressList.as_view()),
    url(r'^media_detail/$', views.MediaDetail.as_view()),
    url(r'^media_list/$', views.MediaList.as_view()),

    url(r'^information_detail/$', views.InformationDetail.as_view()),
    url(r'^information_list/$', views.InformationList.as_view()),

    url(r'^case_detail/$', views.CaseDetail.as_view()),
    url(r'^case_list/$', views.CaseList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


