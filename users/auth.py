from users.models import User
from django.utils.timezone import now


class UserBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(phone=username, is_active=1)
        except User.DoesNotExist:
            pass
        else:
            if user.check_password(password):
                user.last_login = now()
                user.save()
                return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id, is_active=1)
        except User.DoesNotExist:
            return None
