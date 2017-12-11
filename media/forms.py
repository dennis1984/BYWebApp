# -*- encoding: utf-8 -*-
from horizon import forms


class MediaTypeListForm(forms.Form):
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class ThemeTypeListForm(forms.Form):
    media_type_id = forms.IntegerField(min_value=1)
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class ProgressListForm(forms.Form):
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class MediaListForm(forms.Form):
    media_type_id = forms.IntegerField(min_value=1, required=False)
    theme_type_id = forms.IntegerField(min_value=1, required=False)
    progress_id = forms.IntegerField(min_value=1, required=False)
    mark = forms.ChoiceField(choices=((0, 1),
                                      (1, 1)),
                             required=False)
    sort = forms.ChoiceField(choices=(('temperature', 1),
                                      ('created', 2),
                                      ('air_time', 3)),
                             error_messages={
                                 'required': 'Params [sort] must in '
                                             '["temperature", "created", "air_time"].'
                             },
                             required=False)
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class MediaDetailForm(forms.Form):
    id = forms.IntegerField(min_value=1)


class InformationDetailForm(forms.Form):
    id = forms.IntegerField(min_value=1)


class InformationListForm(forms.Form):
    # 运营标记：0：无标示 1：重磅发布
    mark = forms.IntegerField(min_value=1, required=False)
    # 栏目：1：最新发布 2：电影大事件 3：娱乐营销观察 4：影片资讯
    column = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class CaseDetailForm(forms.Form):
    id = forms.IntegerField(min_value=1)


class CaseListForm(forms.Form):
    # 运营标记：0：无标示 1：重磅发布
    mark = forms.IntegerField(min_value=1, required=False)
    # 栏目：1：最新发布 2：电影大事件 3：娱乐营销观察 4：影片资讯
    column = forms.IntegerField(min_value=1, required=False)
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class SourceLikeActionForm(forms.Form):
    source_type = forms.IntegerField(min_value=1)
    source_id = forms.IntegerField(min_value=1)


class AdvertResourceListForm(forms.Form):
    source_type = forms.ChoiceField(choices=((1, 1),
                                             (2, 2),
                                             (3, 3)),
                                    error_messages={
                                        'required': 'Param source_type must in [1, 2, 3]'
                                    })
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class RelevantCaseForMediaForm(forms.Form):
    media_id = forms.IntegerField(min_value=1)


class RecommendMediaForm(forms.Form):
    media_id = forms.IntegerField(min_value=1)


class RelevantInformationListForm(forms.Form):
    information_id = forms.IntegerField(min_value=1)
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class RelevantCaseListForm(forms.Form):
    case_id = forms.IntegerField(min_value=1)
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class SearchResourceActionForm(forms.Form):
    # 资源类型： 1：资源 2：案例 3：资讯
    source_type = forms.ChoiceField(choices=((1, 1),
                                             (2, 2),
                                             (3, 3)),
                                    error_messages={
                                        'required': 'Param source_type must in [1, 2, 3]'
                                    })
    # 搜索关键词
    keywords = forms.CharField(max_length=200)

