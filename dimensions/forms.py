# -*- encoding: utf-8 -*-
from horizon import forms


class DimensionListForm(forms.Form):
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class TagsListForm(forms.Form):
    dimension_id = forms.IntegerField(min_value=1)
    count = forms.IntegerField(min_value=1)
