# -*- coding:utf8 -*-
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from reports import views

urlpatterns = [
    url(r'^report_list/$', views.ReportList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
