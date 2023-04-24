from accounts.models import Accounts
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    @staticmethod
    def authenticate(request, phone_number=None,password=None ,**kwargs):
        try:

            user = Accounts.objects.get(phone_number=phone_number,password=password)

        except Accounts.DoesNotExist:
            return None
        else:
            if user.password == password:
                return user
        return None
