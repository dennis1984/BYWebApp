# -*- encoding: utf-8 -*-
from horizon import forms


class CollectActionForm(forms.Form):
    source_type = forms.ChoiceField(choices=((1, 1),
                                             (2, 2),
                                             (3, 3)),
                                    error_messages={
                                        'required': 'Source type must in [1, 2, 3]'
                                    })
    source_id = forms.IntegerField(min_value=1)


class CollectDeleteForm(forms.Form):
    id = forms.IntegerField(min_value=1)


class CollectListForm(forms.Form):
    source_type = forms.ChoiceField(choices=((0, 1),
                                             (1, 2),
                                             (2, 3),
                                             (3, 4)),
                                    error_messages={
                                        'required': 'Source type must in [0, 1, 2, 3]'
                                    },
                                    required=False)
    page_index = forms.IntegerField(min_value=1, required=False)
    page_size = forms.IntegerField(min_value=1, required=False)

