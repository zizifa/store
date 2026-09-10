from accounts.models import Accounts
from django.contrib.auth.backends import ModelBackend


class PhoneOTPBackend(ModelBackend):
    """Backend for phone number + OTP authentication."""
    
    def authenticate(self, request, phone_number=None, password=None, **kwargs):
        """
        Authenticate user with phone number and password (for staff).
        For OTP authentication, use the OTPChallenge model directly.
        """
        if not phone_number:
            return None
        
        try:
            user = Accounts.objects.get(phone_number=phone_number)
        except Accounts.DoesNotExist:
            return None
        
        # For staff authentication, use password verification
        if user.is_staff or user.is_superuser:
            if password and user.check_password(password):
                return user
        
        return None
