# -*- encoding: utf-8 -*-
from horizon import forms


class PhoneForm(forms.Form):
    phone = forms.CharField(max_length=20, min_length=11,
                            error_messages={
                                'required': u'手机号不能为空',
                                'min_length': u'手机号位数不够'
                            })


class PasswordForm(forms.Form):
    password = forms.CharField(min_length=6,
                               max_length=50,
                               error_messages={
                                   'required': u'密码不能为空',
                                   'min_length': u'密码长度不能少于6位'
                               })
    # confirm_password = forms.CharField(min_length=6,
    #                                    max_length=50,
    #                                    error_messages={
    #                                        'required': u'密码不能为空',
    #                                        'min_length': u'密码长度不能少于6位'
    #                                    })


class SendIdentifyingCodeForm(forms.Form):
    """
    发送手机/邮箱验证码（未登录状态）
    """
    username_type = forms.ChoiceField(choices=(('phone', 1),
                                               ('email', 2)))
    username = forms.CharField(max_length=200)
    method = forms.ChoiceField(choices=(('register', 1),
                                        ('forget_password', 2)),
                               error_messages={
                                   'required': u'method 值必须为["register","forget_password"]之一。',
                               })


class SendIdentifyingCodeWithLoginForm(forms.Form):
    """
    发送手机/邮箱验证码（登录状态）
    """
    username_type = forms.ChoiceField(choices=(('phone', 1),
                                               ('email', 2)))
    # username = forms.CharField(max_length=200)


class VerifyIdentifyingCodeForm(PhoneForm):
    """
    验证手机验证码
    """
    identifying_code = forms.CharField(max_length=10,
                                       error_messages={'required': u'验证码不能为空'})


class UpdateUserInfoForm(forms.Form):
    """
    更改用户信息
    """
    password = forms.CharField(min_length=6, max_length=50, required=False)
    nickname = forms.CharField(max_length=100, required=False)
    gender = forms.IntegerField(min_value=1, max_value=2, required=False)
    birthday = forms.DateField(required=False)
    province = forms.CharField(max_length=16, required=False)
    city = forms.CharField(max_length=32, required=False)
    head_picture = forms.ImageField(required=False)
    role_id = forms.IntegerField(required=False)


class CreateUserForm(PasswordForm):
    """
    用户注册
    """
    username_type = forms.ChoiceField(choices=(('phone', 1),
                                               ('email', 2)))
    username = forms.CharField(max_length=200)
    identifying_code = forms.CharField(min_length=6, max_length=10,
                                       error_messages={
                                           'required': u'验证码不能为空'
                                       })


class EmailForm(forms.Form):
    email = forms.EmailField(max_length=200)


class SetPasswordForm(CreateUserForm):
    """
    忘记密码
    """


class BindingActionForm(forms.Form):
    """
    绑定用户手机号、邮箱等
    """
    username_type = forms.ChoiceField(choices=(('phone', 1),
                                               ('email', 2)))
    username = forms.CharField(max_length=200)
    identifying_code = forms.CharField(max_length=10, required=False)


class AdvertListForm(forms.Form):
    food_court_id = forms.IntegerField(min_value=1)
    ad_position_name = forms.CharField(max_length=20, required=False)


class WXAuthLoginForm(forms.Form):
    callback_url = forms.CharField(max_length=256, required=False)


class WBAuthLoginForm(forms.Form):
    callback_url = forms.CharField(max_length=256, required=False)
