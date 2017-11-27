# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from oauth2_provider.views.mixins import OAuthLibMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import View
from django.conf import settings

from users.serializers import (UserSerializer,
                               UserInstanceSerializer,
                               UserDetailSerializer,
                               UserListSerializer,
                               IdentifyingCodeSerializer,
                               RoleListSerializer)
from users.permissions import IsOwnerOrReadOnly
from users.models import (User,
                          make_token_expire,
                          IdentifyingCode,
                          Role)
from users.forms import (CreateUserForm,
                         SendIdentifyingCodeForm,
                         SendIdentifyingCodeWithLoginForm,
                         VerifyIdentifyingCodeForm,
                         UpdateUserInfoForm,
                         UpdateUserPasswordWithLoginForm,
                         SetPasswordForm,
                         BindingActionForm,
                         WXAuthLoginForm,
                         WBAuthLoginForm,
                         PhoneForm,
                         EmailForm)
from users.wx_auth.views import Oauth2AccessToken

from horizon.views import APIView
from horizon.main import make_random_number_of_string
from horizon import main
import copy
import urllib


def verify_identifying_code(params_dict):
    """
    验证验证码
    """
    username = params_dict['username']
    identifying_code = params_dict['identifying_code']

    instance = IdentifyingCode.get_object_by_phone_or_email(username)
    if not instance:
        return False, 'Identifying code is not existed or expired.'
    if instance.identifying_code != identifying_code:
        return False, 'Identifying code is incorrect.'
    return True, None


class IdentifyingCodeAction(APIView):
    """
    send identifying code to a phone
    """
    def verify_phone(self, cld):
        instance = User.get_object_by_username(username_type=cld['username_type'],
                                               username=cld['username'])
        if cld['method'] == 'register':     # 用户注册
            if isinstance(instance, User):
                return Exception('The phone or email is already registered.')
        elif cld['method'] == 'forget_password':   # 忘记密码
            if isinstance(instance, Exception):
                return Exception('The user of the phone or email is not existed.')
        else:
            return Exception('Parameters Error.')
        return True

    def is_request_data_valid(self, **kwargs):
        if kwargs['username_type'] == 'phone':
            form = PhoneForm({'phone': kwargs['username']})
            if not form.is_valid():
                return False, form.errors
        elif kwargs['username_type'] == 'email':
            form = EmailForm({'email': kwargs['username']})
            if not form.is_valid():
                return False, form.errors
        return True, None

    def send_identifying_code(self, identifying_code, **kwargs):
        # 发送到短信平台
        if kwargs['username_type'] == 'phone':
            main.send_message_to_phone({'code': identifying_code},
                                       (kwargs['username'],))
        elif kwargs['username_type'] == 'email':
            # 发送邮件
            _to = [kwargs['username']]
            subject = '验证码'
            text = '您的验证码是%s, 15分钟有效。' % identifying_code
            main.send_email(_to, subject, text)

    def post(self, request, *args, **kwargs):
        """
        发送验证码
        """
        form = SendIdentifyingCodeForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(**cld)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)
        result = self.verify_phone(cld)
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)

        identifying_code = make_random_number_of_string(str_length=6)
        serializer = IdentifyingCodeSerializer(data={'phone_or_email': cld['username'],
                                                     'identifying_code': identifying_code})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        # 发送验证码
        self.send_identifying_code(identifying_code, **cld)
        return Response(status=status.HTTP_200_OK)


class IdentifyingCodeActionWithLogin(generics.GenericAPIView):
    """
    发送短信验证码（登录状态）
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def send_identifying_code(self, identifying_code, **kwargs):
        # 发送到短信平台
        if kwargs['username_type'] == 'phone':
            main.send_message_to_phone({'code': identifying_code},
                                       (kwargs['username'],))
        elif kwargs['username_type'] == 'email':
            # 发送邮件
            _to = [kwargs['username']]
            subject = '验证码'
            text = '您的验证码是%s, 15分钟有效。' % identifying_code
            main.send_email(_to, subject, text)

    def is_request_data_valid(self, request, **kwargs):
        if 'username' in kwargs:
            if kwargs['username_type'] == 'phone':
                if request.user.is_binding(kwargs['username_type']):
                    if kwargs['username'] != request.user.phone:
                        return False, 'The phone number is incorrect.'
                else:
                    user = User.get_object_by_username(**kwargs)
                    if isinstance(user, User):
                        return False, 'The phone number is already binding.'
            elif kwargs['username_type'] == 'email':
                if request.user.is_binding(kwargs['username_type']):
                    if kwargs['username'] != request.user.email:
                        return False, 'The email is incorrect.'
                else:
                    user = User.get_object_by_username(**kwargs)
                    if isinstance(user, User):
                        return False, 'The email is already binding.'
        else:
            if not request.user.is_binding(kwargs['username_type']):
                return False, 'Your phone or email is not existed.'
        return True, None

    def post(self, request, *args, **kwargs):
        form = SendIdentifyingCodeWithLoginForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(request, **cld)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        if 'username' not in cld:
            if cld['username_type'] == 'phone':
                cld['username'] = request.user.phone
            else:
                cld['username'] = request.user.email
        identifying_code = make_random_number_of_string(str_length=6)
        serializer = IdentifyingCodeSerializer(data={'phone_or_email': cld['username'],
                                                     'identifying_code': identifying_code})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        self.send_identifying_code(identifying_code, **cld)
        return Response(status=status.HTTP_200_OK)


class IdentifyingCodeVerify(APIView):
    def post(self, request, *args, **kwargs):
        """
        验证手机验证码
        """
        form = VerifyIdentifyingCodeForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)
        cld = form.cleaned_data
        is_valid, error_message = verify_identifying_code(cld)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Result': is_valid}, status=status.HTTP_200_OK)


class UserNotLoggedAction(APIView):
    """
    create user API
    """
    def get_object_by_username(self, username_type, username):
        if username_type == 'phone':
            return User.get_object(**{'phone': username})
        elif username_type == 'email':
            return User.get_object(**{'email': username})
        else:
            return Exception('Params is incorrect.')

    def is_request_data_valid(self, **kwargs):
        if kwargs['username_type'] == 'phone':
            form = PhoneForm({'phone': kwargs['username']})
            if not form.is_valid():
                return False, form.errors
        elif kwargs['username_type'] == 'email':
            form = EmailForm({'email': kwargs['username']})
            if not form.is_valid():
                return False, form.errors
        return True, None

    def get_perfect_request_data(self, **kwargs):
        kwargs['nickname'] = kwargs['username']
        kwargs.pop('identifying_code')
        return kwargs

    def post(self, request, *args, **kwargs):
        """
        用户注册
        """
        form = CreateUserForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(**cld)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)
        is_valid, error_message = verify_identifying_code(cld)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        init_data = self.get_perfect_request_data(**cld)
        try:
            user = User.objects.create_user(**init_data)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        # 置用户为登录状态
        _token = Oauth2AccessToken().get_token(user)
        return Response(_token, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        忘记密码
        """
        form = SetPasswordForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        is_valid, error_message = verify_identifying_code(cld)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object_by_username(cld['username_type'], cld['username'])
        if isinstance(instance, Exception):
            return Response({'Detail': instance.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(instance)
        try:
            serializer.update_password(request, instance, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        # serializer_response = UserInstanceSerializer(instance)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)


class UserAction(generics.GenericAPIView):
    """
    update user API
    """
    permission_classes = (IsOwnerOrReadOnly, )

    def get_perfect_validate_data(self, **cleaned_data):
        if 'role_id' in cleaned_data:
            role = Role.get_object(pk=cleaned_data['role_id'])
            cleaned_data['role'] = role.name
            cleaned_data.pop('role_id')
        return cleaned_data

    def put(self, request, *args, **kwargs):
        """
        更新用户信息
        """
        form = UpdateUserInfoForm(request.data, request.FILES)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        cld = self.get_perfect_validate_data(**cld)
        serializer = UserSerializer(request.user)
        try:
            serializer.update_userinfo(request, request.user, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    def patch(self, request, *args, **kwargs):
        """
        更改用户密码
        """
        form = UpdateUserPasswordWithLoginForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        result = False
        error_message = None
        for username in [request.user.phone, request.user.email]:
            params_dict = {'username': username,
                           'identifying_code': cld['identifying_code']}
            is_valid, error_message = verify_identifying_code(params_dict)
            if is_valid:
                result = is_valid
                break
        if not result:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(request.user)
        try:
            serializer.update_password(request, request.user, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)


class UserDetail(generics.GenericAPIView):
    permission_classes = (IsOwnerOrReadOnly, )

    def get_user_object(self, request):
        return User.get_user_detail(request)

    def post(self, request, *args, **kwargs):
        user_detail = self.get_user_object(request)
        if isinstance(user_detail, Exception):
            return Response({'Detail': user_detail.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserDetailSerializer(data=user_detail)
        if not serializer.is_valid():
            return Response({'Detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WXAuthAction(APIView):
    def get(self, request, *args, **kwargs):
        """
        微信第三方登录授权
        """
        from users.wx_auth import settings as wx_auth_settings
        from users.wx_auth.serializers import RandomStringSerializer

        form = WXAuthLoginForm(getattr(request, request.method))
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        wx_auth_params = copy.deepcopy(wx_auth_settings.WX_AUTH_PARAMS['get_code'])
        wx_auth_url = wx_auth_settings.WX_AUTH_URLS['get_code']
        end_params = wx_auth_params.pop('end_params')
        state = wx_auth_params['state']()
        wx_auth_params['state'] = state
        wx_auth_params['redirect_uri'] = urllib.quote_plus(
            wx_auth_params['redirect_uri'] % cld.get('callback_url', ''))
        return_url = '%s?%s%s' % (wx_auth_url,
                                  main.make_dict_to_verify_string(wx_auth_params),
                                  end_params)
        serializer = RandomStringSerializer(data={'random_str': state})
        if serializer.is_valid():
            serializer.save()
            return_data = {'wx_auth_url': return_url}
            return Response(return_data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class WBAuthAction(APIView):
    def get(self, request, *args, **kwargs):
        """
        微博第三方登录授权
        """
        from users.wb_auth import settings as wb_auth_settings
        from users.wb_auth.serializers import RandomStringSerializer

        form = WBAuthLoginForm(getattr(request, request.method))
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        wb_auth_params = copy.deepcopy(wb_auth_settings.WB_AUTH_PARAMS['get_code'])
        wb_auth_url = wb_auth_settings.WB_AUTH_URLS['get_code']
        state = wb_auth_params['state']()
        wb_auth_params['state'] = state
        wb_auth_params['redirect_uri'] = urllib.quote_plus(
            wb_auth_params['redirect_uri'] % cld.get('callback_url', ''))
        return_url = '%s?%s' % (wb_auth_url,
                                main.make_dict_to_verify_string(wb_auth_params))
        serializer = RandomStringSerializer(data={'random_str': state})
        if serializer.is_valid():
            serializer.save()
            return_data = {'wb_auth_url': return_url}
            return Response(return_data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserBindingAction(generics.GenericAPIView):
    """
    绑定手机号、邮箱及微博等
    """
    def get_object_by_openid(self, out_open_id):
        return User.get_object(**{'out_open_id': out_open_id})

    def is_request_data_valid(self, **kwargs):
        if kwargs['username_type'] == 'phone':
            form = PhoneForm({'phone': kwargs['username']})
            if not form.is_valid():
                return False, form.errors
        elif kwargs['username_type'] == 'email':
            form = EmailForm({'email': kwargs['username']})
            if not form.is_valid():
                return False, form.errors
        return True, None

    def post(self, request, *args, **kwargs):
        """
        绑定动作
        """
        form = BindingActionForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        is_valid, error_message = self.is_request_data_valid(**cld)
        if not is_valid:
            return Response({'Detail': error_message}, status=status.HTTP_400_BAD_REQUEST)
        result = verify_identifying_code(cld)
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_binding(cld['username_type']):
            return Response({'Detail': 'The phone/email is already binding'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(request.user)
        try:
            serializer.binding_phone_or_email_to_user(request, request.user, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class AuthLogin(OAuthLibMixin, View):
    """
    用户认证：登录
    """
    def post(self, request, *args, **kwargs):
        return redirect(reverse('oauth2_provider.token'))


class AuthLogout(generics.GenericAPIView):
    """
    用户认证：登出
    """
    def post(self, request, *args, **kwargs):
        make_token_expire(request)
        return Response(status=status.HTTP_200_OK)


class RoleList(generics.GenericAPIView):
    """
    用户角色列表
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def get_role_list(self):
        return Role.filter_objects()

    def post(self, request, *args, **kwargs):
        role = self.get_role_list()

        serializer = RoleListSerializer(role)
        data_list = serializer.list_data()
        if isinstance(data_list, Exception):
            return Response({'Detail': data_list.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data_list, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
