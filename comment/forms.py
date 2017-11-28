# -*- encoding: utf-8 -*-
from horizon import forms


class CommentInputForm(forms.Form):
    source_type = forms.ChoiceField(choices=((1, 1),
                                             (2, 2),
                                             (3, 3)),
                                    error_messages={
                                        'required': 'Source type must in [1, 2, 3]'
                                    })
    source_id = forms.IntegerField(min_value=1)
    content = forms.CharField(max_length=170)


class CommentListForm(forms.Form):
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)


class CommentDetailForm(forms.Form):
    id = forms.CharField(min_length=10, max_length=32)


class CommentDeleteForm(forms.Form):
    id = forms.IntegerField(min_value=1)
