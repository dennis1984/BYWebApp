# -*- encoding: utf-8 -*-
from horizon import forms


class DimensionListForm(forms.Form):
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class TagsListForm(forms.Form):
    dimension_id = forms.IntegerField(min_value=1)
    count = forms.IntegerField(min_value=1)


class ResourceMatchActionForm(forms.Form):
    first_dimension_id = forms.IntegerField(min_value=1)
    # tags_list：标签列表，数据格式为JSON，数据示例：
    # [{'tag_ids': [1, 2, 3, xxx],
    #   'dimension_id': 1,
    #   'is_default_tag': false}, ...
    # ]
    tags_list = forms.CharField()
