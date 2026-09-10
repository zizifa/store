from datetime import timedelta
from typing import Optional
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class AccountsManager(BaseUserManager):
    def normalize_phone(self, phone: str) -> str:
        """Normalize phone to E.164 canonical string."""
        from phonenumber_field.phonenumber import to_python
        p = to_python(phone, region='IR')
        if not p or not p.is_valid():
            raise ValidationError('Invalid phone number')
        return p.as_e164

    def create_user(
        self,
        phone_number: str,
        password: Optional[str] = None,
        **extra_fields,
    ):
        if not phone_number:
            raise ValueError('Phone number must be set')
        phone_number = self.normalize_phone(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        phone_number: str,
        password: Optional[str] = None,
        **extra_fields,
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class Accounts(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    username = models.CharField(max_length=50, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True)
    phone_number = PhoneNumberField(unique=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    # Django auth flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = AccountsManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number.as_e164 if self.phone_number else 'Anonymous'

    def get_full_name(self):
        return f'{self.first_name.strip()} {self.last_name.strip()}'.strip()

    def get_short_name(self):
        return self.first_name.strip() or self.phone_number.as_e164

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        # Delegate to PermissionsMixin so group/user permissions keep working.
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        return super().has_module_perms(app_label)


class OTPChallenge(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = 'LOGIN', 'Login'
        PHONE_CHANGE = 'PHONE_CHANGE', 'Phone change'
        RECOVERY = 'RECOVERY', 'Account recovery'

    phone_number = PhoneNumberField(null=False, blank=False)
    purpose = models.CharField(max_length=20, choices=Purpose.choices)

    code_hash = models.CharField(max_length=128, null=False, blank=False)
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)

    expires_at = models.DateTimeField(null=False, blank=False)
    locked_until = models.DateTimeField(blank=True, null=True)

    consumed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['phone_number', 'purpose', 'expires_at', 'consumed_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['phone_number', 'purpose'],
                name='unique_active_otp_per_phone_purpose',
                condition=models.Q(consumed_at__isnull=True, locked_until__isnull=True),
            ),
        ]

    def __str__(self):
        status = 'consumed' if self.consumed_at else 'active'
        return f'{self.phone_number.as_e164} {self.purpose} ({status})'

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def is_locked(self) -> bool:
        if not self.locked_until:
            return False
        return timezone.now() < self.locked_until

    def increment_attempts(self):
        self.attempts = models.F('attempts') + 1
        self.save(update_fields=['attempts', 'updated_at'])
        self.refresh_from_db(fields=['attempts'])

    def lock(self):
        self.locked_until = timezone.now() + timedelta(minutes=15)
        self.save(update_fields=['locked_until', 'updated_at'])

    def consume(self):
        self.consumed_at = timezone.now()
        self.save(update_fields=['consumed_at', 'updated_at'])

    @classmethod
    def create_for_phone(cls, phone: str, purpose: str) -> 'OTPChallenge':
        """Thin compatibility delegate; logic lives in the OTP service."""
        from accounts.services.otp import otp_service
        return otp_service.create_challenge(phone, purpose)

    @classmethod
    def verify(cls, phone: str, purpose: str, code: str) -> Optional['Accounts']:
        """Thin compatibility delegate; logic lives in the OTP service."""
        from accounts.services.otp import otp_service
        return otp_service.verify_otp(phone, purpose, code)


class Profile(models.Model):
    user = models.OneToOneField(Accounts, on_delete=models.CASCADE)
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.first_name or self.user.phone_number.as_e164

    def full_address(self):
        return f'{self.city}, {self.state}, {self.address}'
