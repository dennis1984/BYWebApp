# -*- encoding: utf-8 -*-
from horizon import forms


class ScoreRecordListForm(forms.Form):
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)

