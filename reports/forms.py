# -*- encoding: utf-8 -*-
from horizon import forms


class ReportListForm(forms.Form):
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class ReportFileDownloadForm(forms.Form):
    media_id = forms.IntegerField(min_value=1)
