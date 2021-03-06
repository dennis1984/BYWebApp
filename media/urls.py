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
    # 相关案例
    url(r'^relevant_case_for_media/$', views.RelevantCaseForMedia.as_view()),
    # 推荐资源
    url(r'^recommend_media_list/$', views.RecommendMediaList.as_view()),

    url(r'^information_detail/$', views.InformationDetail.as_view()),
    url(r'^information_list/$', views.InformationList.as_view()),
    url(r'^relevant_information_list/$', views.RelevantInformationList.as_view()),
    url(r'^next_information_detail/$', views.InformationDetailForNext.as_view()),

    url(r'^case_detail/$', views.CaseDetail.as_view()),
    url(r'^case_list/$', views.CaseList.as_view()),
    url(r'^relevant_case_list/$', views.RelevantCaseList.as_view()),
    url(r'^next_case_detail/$', views.CaseDetailForNext.as_view()),

    url(r'^like_action/$', views.SourceLikeAction.as_view()),
    # 轮播广告
    url(r'^advert_resource_list/$', views.AdvertResourceList.as_view()),
    # 资源搜索
    url(r'^search_resource_list/$', views.SearchResourceAction.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


