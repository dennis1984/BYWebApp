# -*- coding:utf8 -*-
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from dimensions import views

urlpatterns = [
    url(r'^dimension_list/$', views.DimensionList.as_view()),
    url(r'^tag_list/$', views.TagList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


