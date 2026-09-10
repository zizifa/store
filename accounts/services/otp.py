"""OTP service layer for secure one-time password operations.

This module is the SINGLE source of truth for OTP business logic:
generation, hashing, expiry, resend cooldown, attempt limits, locking,
consumption and verification orchestration. ``accounts.models.OTPChallenge``
holds data/state and exposes only thin compatibility delegates to the logic
implemented here.
"""
import secrets
from datetime import timedelta
from importlib import import_module
from typing import Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils import timezone

from accounts.models import Accounts, OTPChallenge


class OTPServiceError(Exception):
    """Base exception for OTP service errors."""
    pass


# ---------------------------------------------------------------------------
# OTP primitives (single source of truth)
# ---------------------------------------------------------------------------

def generate_otp(length: Optional[int] = None) -> str:
    """Generate a cryptographically secure numeric OTP."""
    if length is None:
        length = getattr(settings, 'OTP_LENGTH', 6)
    digits = '0123456789'
    return ''.join(secrets.choice(digits) for _ in range(length))


def hash_otp(otp: str) -> str:
    """Hash OTP using Django's password hashing utilities."""
    from django.contrib.auth.hashers import make_password
    return make_password(otp)


def verify_otp_hash(otp: str, hashed: str) -> bool:
    """Verify OTP against stored hash."""
    from django.contrib.auth.hashers import check_password
    return check_password(otp, hashed)


# ---------------------------------------------------------------------------
# SMS provider abstraction and production-safe selection
# ---------------------------------------------------------------------------

class SMSProvider:
    def send_otp(self, phone_number: str, code: str) -> None:
        raise NotImplementedError


class ConsoleSMSProvider(SMSProvider):
    """Development/testing provider. Prints the code; NEVER for production."""

    def send_otp(self, phone_number: str, code: str) -> None:
        print(f'[ConsoleSMS] Sending OTP {code} to {phone_number}')


def get_sms_provider() -> SMSProvider:
    """Resolve the configured SMS provider.

    - ``SMS_PROVIDER`` setting: the literal ``'console'`` or a dotted path to
      an :class:`SMSProvider` subclass (e.g. ``'myapp.sms.VendorProvider'``).
    - ``DEBUG=True``: defaults to the console provider when unconfigured.
    - ``DEBUG=False``: missing provider, the console provider, or an
      unresolvable/unsupported provider raises :class:`ImproperlyConfigured`
      instead of silently exposing OTP codes.
    """
    configured = getattr(settings, 'SMS_PROVIDER', None)
    debug = getattr(settings, 'DEBUG', False)

    if not configured:
        if debug:
            return ConsoleSMSProvider()
        raise ImproperlyConfigured(
            'SMS_PROVIDER is not configured. Set SMS_PROVIDER to a dotted '
            'path of an SMSProvider implementation before running with '
            'DEBUG=False.'
        )

    if configured == 'console':
        if debug:
            return ConsoleSMSProvider()
        raise ImproperlyConfigured(
            'SMS_PROVIDER="console" is not allowed when DEBUG=False: it '
            'would expose OTP codes. Configure a real SMS provider.'
        )

    module_path, _, attr = configured.rpartition('.')
    if not module_path:
        raise ImproperlyConfigured(
            f'SMS_PROVIDER must be a dotted path or "console", got {configured!r}.'
        )
    try:
        provider_cls = getattr(import_module(module_path), attr)
    except (ImportError, AttributeError) as exc:
        raise ImproperlyConfigured(
            f'Could not import SMS_PROVIDER {configured!r}.'
        ) from exc

    if not (isinstance(provider_cls, type) and issubclass(provider_cls, SMSProvider)):
        raise ImproperlyConfigured(
            f'SMS_PROVIDER {configured!r} must subclass '
            'accounts.services.otp.SMSProvider.'
        )
    return provider_cls()


class OTPService:
    """Service class for OTP challenge creation, verification, and management."""
    
    def __init__(self):
        self.max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 5)
        self.ttl_seconds = getattr(settings, 'OTP_TTL_SECONDS', 120)
        self.resend_cooldown_seconds = getattr(settings, 'OTP_RESEND_COOLDOWN_SECONDS', 60)
    
    def create_challenge(self, phone: str, purpose: str = 'LOGIN') -> OTPChallenge:
        """Invalidate previous active challenges, then create a fresh one.

        Owns generation, hashing and expiry. Runs atomically so invalidating
        prior challenges and creating the new one satisfy the unique
        active-challenge constraint together.
        """
        from django.db import transaction

        phone_normalized = Accounts.objects.normalize_phone(phone)
        code = generate_otp(getattr(settings, 'OTP_LENGTH', 6))
        code_hash = hash_otp(code)

        with transaction.atomic():
            # Invalidate any previous active challenges.
            OTPChallenge.objects.filter(
                phone_number=phone_normalized,
                purpose=purpose,
                consumed_at__isnull=True,
            ).update(consumed_at=timezone.now())

            challenge = OTPChallenge.objects.create(
                phone_number=phone_normalized,
                purpose=purpose,
                code_hash=code_hash,
                expires_at=timezone.now() + timedelta(seconds=self.ttl_seconds),
                max_attempts=self.max_attempts,
            )
        challenge._plaintext_code = code
        return challenge
    
    def send_otp(self, phone: str, purpose: str = 'LOGIN') -> tuple[OTPChallenge, str]:
        """Create OTP challenge and send via SMS provider."""
        phone_normalized = Accounts.objects.normalize_phone(phone)

        # Enforce resend cooldown against the most recently sent challenge,
        # BEFORE creating a new one (a new challenge would reset last_sent_at).
        latest = OTPChallenge.objects.filter(
            phone_number=phone_normalized, purpose=purpose
        ).order_by('-created_at').first()
        if latest and latest.last_sent_at:
            cooldown_until = latest.last_sent_at + timedelta(
                seconds=self.resend_cooldown_seconds
            )
            if timezone.now() < cooldown_until:
                raise OTPServiceError(
                    'OTP recently sent. Please wait before requesting a new one.'
                )

        challenge = self.create_challenge(phone_normalized, purpose)
        challenge.last_sent_at = timezone.now()
        challenge.save(update_fields=['last_sent_at'])

        # Send OTP (plaintext code is available as _plaintext_code)
        code = challenge._plaintext_code
        get_sms_provider().send_otp(phone_normalized, code)

        return challenge, code
    
    def verify_otp(self, phone: str, purpose: str, code: str) -> Optional[Accounts]:
        """Verify OTP and return the associated user, consuming the OTP atomically."""
        from django.db import transaction

        phone_normalized = Accounts.objects.normalize_phone(phone)

        with transaction.atomic():
            challenge = OTPChallenge.objects.select_for_update().filter(
                phone_number=phone_normalized,
                purpose=purpose,
                consumed_at__isnull=True,
            ).first()

            if not challenge:
                return None
            if challenge.is_expired():
                return None
            if challenge.is_locked():
                return None
            if challenge.attempts >= challenge.max_attempts:
                return None

            if not verify_otp_hash(code, challenge.code_hash):
                challenge.increment_attempts()
                if challenge.attempts >= challenge.max_attempts:
                    challenge.lock()
                return None

            challenge.consume()

            try:
                user = Accounts.objects.get(phone_number=phone_normalized)
            except Accounts.DoesNotExist:
                user = Accounts.objects.create_user(phone_number=phone_normalized)
            return user
    
    def check_lockout_status(self, phone: str, purpose: str = 'LOGIN') -> bool:
        """Check if phone is currently locked due to too many failed attempts."""
        phone_normalized = Accounts.objects.normalize_phone(phone)
        
        challenge = OTPChallenge.objects.filter(
            phone_number=phone_normalized,
            purpose=purpose,
            consumed_at__isnull=True,
        ).first()
        
        if not challenge:
            return False
        
        return challenge.is_locked()


# Module-level convenience functions
otp_service = OTPService()


def create_otp_challenge(phone: str, purpose: str = 'LOGIN') -> OTPChallenge:
    """Create an OTP challenge for the given phone number."""
    return otp_service.create_challenge(phone, purpose)


def send_otp(phone: str, purpose: str = 'LOGIN') -> tuple[OTPChallenge, str]:
    """Create OTP challenge and send via SMS provider."""
    return otp_service.send_otp(phone, purpose)


def verify_otp(phone: str, purpose: str, code: str) -> Optional[Accounts]:
    """Verify OTP and return the associated user."""
    return otp_service.verify_otp(phone, purpose, code)


def is_phone_locked(phone: str, purpose: str = 'LOGIN') -> bool:
    """Check if phone is currently locked."""
    return otp_service.check_lockout_status(phone, purpose)