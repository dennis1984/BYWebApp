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

