# -*- coding:utf8 -*-
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from score import views

urlpatterns = [
    url(r'^score_detail/$', views.ScoreDetail.as_view()),
    url(r'^score_record_list/$', views.ScoreRecordList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
