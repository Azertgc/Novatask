from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CaseInsensitiveModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get(username__iexact=username)
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            user = UserModel._default_manager.filter(username__iexact=username).order_by('id').first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None