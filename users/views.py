# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from users.serializers import (UserSerializer,
                               UserInstanceSerializer,
                               UserDetailSerializer,
                               UserListSerializer,
                               IdentifyingCodeSerializer)
from users.permissions import IsOwnerOrReadOnly
from users.models import (User,
                          make_token_expire,
                          IdentifyingCode)
from users.forms import (CreateUserForm,
                         SendIdentifyingCodeForm,
                         VerifyIdentifyingCodeForm,
                         UpdateUserInfoForm,
                         SetPasswordForm,
                         WXAuthCreateUserForm,
                         AdvertListForm,
                         WXAuthLoginForm,
                         WBAuthLoginForm)
from users.wx_auth.views import Oauth2AccessToken

from horizon.views import APIView
from horizon.main import make_random_number_of_string
from horizon import main
import copy
import urllib


def verify_identifying_code(params_dict):
    """
    验证手机验证码
    """
    phone = params_dict['phone']
    identifying_code = params_dict['identifying_code']

    instance = IdentifyingCode.get_object_by_phone(phone)
    if not instance:
        return Exception(('Identifying code is not existed or expired.',))
    if instance.identifying_code != identifying_code:
        return Exception(('Identifying code is incorrect.',))
    return True


class IdentifyingCodeAction(APIView):
    """
    send identifying code to a phone
    """
    def verify_phone(self, cld):
        instance = User.get_object(**{'phone': cld['phone']})
        if cld['method'] == 'register':     # 用户注册
            if isinstance(instance, User):
                return Exception(('Error', 'The phone number is already registered.'))
        elif cld['method'] == 'forget_password':   # 忘记密码
            if isinstance(instance, Exception):
                return Exception(('Error', 'The user of the phone number is not existed.'))
        else:
            return Exception(('Error', 'Parameters Error.'))
        return True

    def post(self, request, *args, **kwargs):
        """
        发送验证码
        """
        form = SendIdentifyingCodeForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        result = self.verify_phone(cld)
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)

        identifying_code = make_random_number_of_string(str_length=6)
        serializer = IdentifyingCodeSerializer(data={'phone': cld['phone'],
                                                     'identifying_code': identifying_code})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        # 发送到短线平台
        main.send_message_to_phone({'code': identifying_code}, (cld['phone'],))
        return Response(status=status.HTTP_200_OK)


class IdentifyingCodeActionWithLogin(generics.GenericAPIView):
    """
    发送短信验证码（登录状态）
    """
    permission_classes = (IsOwnerOrReadOnly,)

    def post(self, request, *args, **kwargs):
        phone = request.user.phone
        identifying_code = make_random_number_of_string(str_length=6)
        serializer = IdentifyingCodeSerializer(data={'phone': phone,
                                                     'identifying_code': identifying_code})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        # 发送到短线平台
        main.send_message_to_phone({'code': identifying_code}, (phone,))
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
        result = verify_identifying_code(cld)
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Result': result}, status=status.HTTP_200_OK)


class UserNotLoggedAction(APIView):
    """
    create user API
    """
    def get_object_by_username(self, phone):
        return User.get_object(**{'phone': phone})

    def post(self, request, *args, **kwargs):
        """
        用户注册
        """
        form = CreateUserForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        result = verify_identifying_code(cld)
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.create_user(**cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserInstanceSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        忘记密码
        """
        form = SetPasswordForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        result = verify_identifying_code(cld)
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object_by_username(cld['phone'])
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

    def get_object_of_user(self, request):
        return User.get_object(**{'pk': request.user.id})

    def put(self, request, *args, **kwargs):
        """
        更新用户信息
        """
        form = UpdateUserInfoForm(request.data, request.FILES)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        obj = self.get_object_of_user(request)
        if isinstance(obj, Exception):
            return Response({'Detail': obj.args}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(obj)
        try:
            serializer.update_userinfo(request, obj, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer_response = UserInstanceSerializer(obj)
        return Response(serializer_response.data, status=status.HTTP_206_PARTIAL_CONTENT)


class UserDetail(generics.GenericAPIView):
    permission_classes = (IsOwnerOrReadOnly, )

    def post(self, request, *args, **kwargs):
        user = User.get_user_detail(request)
        if isinstance(user, Exception):
            return Response({'Error': user.args}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserDetailSerializer(user)
        # if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    def post(self, request, *args, **kwargs):
        """
        绑定动作
        """
        form = WXAuthCreateUserForm(request.data)
        if not form.is_valid():
            return Response({'Detail': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        cld = form.cleaned_data
        result = verify_identifying_code(cld)
        if isinstance(result, Exception):
            return Response({'Detail': result.args}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_binding:
            return Response({'Detail': 'The phone is already binded'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(request.user)
        try:
            serializer.binding_phone_to_user(request, request.user, cld)
        except Exception as e:
            return Response({'Detail': e.args}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AuthLogout(generics.GenericAPIView):
    """
    用户认证：登出
    """
    def post(self, request, *args, **kwargs):
        make_token_expire(request)
        return Response(status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
