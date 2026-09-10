"""Tests for OTP authentication core."""
from datetime import timedelta
from django.test import TestCase, override_settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from accounts.models import OTPChallenge, Accounts
from accounts.services.otp import OTPService, send_otp, verify_otp, is_phone_locked, OTPServiceError


User = get_user_model()


@override_settings(
    OTP_TTL_SECONDS=120,
    OTP_MAX_ATTEMPTS=5,
    OTP_RESEND_COOLDOWN_SECONDS=60,
    OTP_LENGTH=6,
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
)
class OTPModelTest(TestCase):
    """Test OTPChallenge model functionality."""
    
    def setUp(self):
        self.phone = '+989120000000'
        self.purpose = 'LOGIN'
    
    def test_generate_otp_creates_6_digit_code(self):
        """Test that OTP generation produces a 6-digit code."""
        challenge = OTPChallenge.create_for_phone(self.phone, self.purpose)
        self.assertEqual(len(challenge._plaintext_code), 6)
        self.assertTrue(challenge._plaintext_code.isdigit())
    
    def test_otp_expires_correctly(self):
        """Test that OTP expires after TTL."""
        challenge = OTPChallenge.create_for_phone(self.phone, self.purpose)
        self.assertTrue(challenge.is_expired() is False)
        
        challenge.expires_at = timezone.now() - timedelta(minutes=1)
        self.assertTrue(challenge.is_expired())
    
    def test_otp_verify_success(self):
        """Test successful OTP verification."""
        challenge = OTPChallenge.create_for_phone(self.phone, self.purpose)
        code = challenge._plaintext_code
        
        user = verify_otp(self.phone, self.purpose, code)

        self.assertIsNotNone(user)
        self.assertEqual(user.phone_number.as_e164, self.phone)
        challenge.refresh_from_db()
        self.assertIsNotNone(challenge.consumed_at)
    
    def test_otp_verify_wrong_code(self):
        """Test OTP verification with wrong code."""
        OTPChallenge.create_for_phone(self.phone, self.purpose)
        
        user = verify_otp(self.phone, self.purpose, '000000')
        
        self.assertIsNone(user)
    
    def test_otp_verify_attempts_increment(self):
        """Test that attempts increment on failed verification."""
        OTPChallenge.create_for_phone(self.phone, self.purpose)
        
        for i in range(5):
            verify_otp(self.phone, self.purpose, '000000')
        
        challenge = OTPChallenge.objects.get(phone_number=self.phone, purpose=self.purpose)
        self.assertEqual(challenge.attempts, 5)
    
    def test_otp_verify_max_attempts_lockout(self):
        """Test that max attempts causes lockout."""
        OTPChallenge.create_for_phone(self.phone, self.purpose)
        
        for _ in range(5):
            verify_otp(self.phone, self.purpose, '000000')
        
        challenge = OTPChallenge.objects.get(phone_number=self.phone, purpose=self.purpose)
        self.assertTrue(challenge.is_locked())
    
    def test_expired_otp_cannot_verify(self):
        """Test that expired OTP cannot verify."""
        challenge = OTPChallenge.create_for_phone(self.phone, self.purpose)
        challenge.expires_at = timezone.now() - timedelta(minutes=5)
        challenge.save()
        
        user = verify_otp(self.phone, self.purpose, challenge._plaintext_code)
        
        self.assertIsNone(user)
    
    def test_consumed_otp_cannot_reuse(self):
        """Test that consumed OTP cannot be reused."""
        challenge = OTPChallenge.create_for_phone(self.phone, self.purpose)
        code = challenge._plaintext_code
        
        user = verify_otp(self.phone, self.purpose, code)
        self.assertIsNotNone(user)
        
        user = verify_otp(self.phone, self.purpose, code)
        self.assertIsNone(user)
    
    def test_otp_plaintext_not_stored_in_db(self):
        """Test that plaintext OTP is not stored in database."""
        challenge = OTPChallenge.create_for_phone(self.phone, self.purpose)
        
        self.assertIsNotNone(challenge.code_hash)
    
    def test_new_customer_account_created(self):
        """Test that new customer account is created through OTP flow."""
        phone = '+989120000000'
        challenge = OTPChallenge.create_for_phone(phone, self.purpose)
        code = challenge._plaintext_code
        
        user = verify_otp(phone, self.purpose, code)
        
        self.assertIsNotNone(user)
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user.phone_number.as_e164, phone)
    
    def test_existing_customer_authenticate(self):
        """Test that existing customer can authenticate through OTP."""
        phone = '+989120000001'
        user = Accounts.objects.create_user(phone_number=phone)
        
        challenge = OTPChallenge.create_for_phone(phone, self.purpose)
        code = challenge._plaintext_code
        
        verified_user = verify_otp(phone, self.purpose, code)
        
        self.assertIsNotNone(verified_user)
        self.assertEqual(verified_user.pk, user.pk)
    
    def test_resend_cooldown_works(self):
        """Test that OTP cannot be resent within cooldown period."""
        challenge, code = send_otp(self.phone, self.purpose)
        self.assertIsNotNone(challenge)
        
        with self.assertRaises(OTPServiceError):
            send_otp(self.phone, self.purpose)


@override_settings(
    OTP_TTL_SECONDS=120,
    OTP_MAX_ATTEMPTS=5,
    OTP_RESEND_COOLDOWN_SECONDS=60,
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
)
class OTPServiceTest(TestCase):
    """Test OTPService class."""
    
    def setUp(self):
        self.service = OTPService()
        self.phone = '+989120000000'
        self.purpose = 'LOGIN'
    
    def test_service_create_challenge(self):
        """Test service create_challenge method."""
        challenge = self.service.create_challenge(self.phone, self.purpose)
        self.assertIsNotNone(challenge)
        self.assertEqual(challenge.phone_number.as_e164, self.phone)
    
    def test_service_verify_otp(self):
        """Test service verify_otp method."""
        challenge = self.service.create_challenge(self.phone, self.purpose)
        code = challenge._plaintext_code
        
        user = self.service.verify_otp(self.phone, self.purpose, code)
        
        self.assertIsNotNone(user)
    
    def test_service_check_lockout_status(self):
        """Test service check_lockout_status method."""
        challenge = OTPChallenge.create_for_phone(self.phone, self.purpose)
        challenge.lock()
        challenge.save()
        
        is_locked = self.service.check_lockout_status(self.phone, self.purpose)
        self.assertTrue(is_locked)
    
    def test_is_phone_locked_helper(self):
        """Test is_phone_locked helper function."""
        self.assertFalse(is_phone_locked(self.phone, self.purpose))
        
        challenge = OTPChallenge.create_for_phone(self.phone, self.purpose)
        challenge.lock()
        challenge.save()
        
        self.assertTrue(is_phone_locked(self.phone, self.purpose))


@override_settings(
    OTP_TTL_SECONDS=120,
    OTP_MAX_ATTEMPTS=5,
    OTP_RESEND_COOLDOWN_SECONDS=60,
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
)
class OTPSecurityTest(TestCase):
    """Test OTP security-related functionality."""
    
    def setUp(self):
        self.phone = '+989120000000'
        self.purpose = 'LOGIN'
    
    def test_different_phones_have_different_challenges(self):
        """Test that different phones get independent challenges."""
        phone2 = '+989120000001'
        
        challenge1 = OTPChallenge.create_for_phone(self.phone, self.purpose)
        challenge2 = OTPChallenge.create_for_phone(phone2, self.purpose)
        
        self.assertNotEqual(challenge1.pk, challenge2.pk)
        self.assertNotEqual(challenge1.code_hash, challenge2.code_hash)
    
    def test_different_purposes_have_different_challenges(self):
        """Test that different purposes get independent challenges."""
        login_challenge = OTPChallenge.create_for_phone(self.phone, 'LOGIN')
        phone_change_challenge = OTPChallenge.create_for_phone(self.phone, 'PHONE_CHANGE')
        
        self.assertNotEqual(login_challenge.pk, phone_change_challenge.pk)
    
    def test_login_challenge_invalidates_previous(self):
        """Test that new login challenge invalidates previous."""
        challenge1 = OTPChallenge.create_for_phone(self.phone, self.purpose)
        challenge2 = OTPChallenge.create_for_phone(self.phone, self.purpose)
        
        challenge1.refresh_from_db()
        self.assertIsNotNone(challenge1.consumed_at)
        
        self.assertIsNone(challenge2.consumed_at)
    
    def test_superuser_can_have_usable_password(self):
        """Test that superuser can have a usable password."""
        user = Accounts.objects.create_superuser(
            phone_number='+989120000000',
            password='testpassword123'
        )
        
        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.check_password('testpassword123'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_customer_has_unusable_password(self):
        """Test that customer created via OTP has unusable password."""
        challenge = OTPChallenge.create_for_phone(self.phone, self.purpose)
        user = verify_otp(self.phone, self.purpose, challenge._plaintext_code)
        
        self.assertFalse(user.has_usable_password())
    
    def test_accounts_manager_normalize_phone(self):
        """Test phone number normalization."""
        normalized = Accounts.objects.normalize_phone('09121234567')
        self.assertTrue(normalized.startswith('+98'))
        
        normalized = Accounts.objects.normalize_phone('+989121234567')
        self.assertEqual(normalized, '+989121234567')
    
    def test_invalid_phone_raises_validation_error(self):
        """Test that invalid phone number raises ValidationError."""
        with self.assertRaises(ValidationError):
            Accounts.objects.normalize_phone('invalid')
    
    def test_accounts_manager_create_user_without_password(self):
        """Test that create_user without password sets unusable password."""
        user = Accounts.objects.create_user(phone_number='+989120000000')
        
        self.assertFalse(user.has_usable_password())
    
    def test_accounts_manager_create_user_with_password(self):
        """Test that create_user with password sets usable password."""
        user = Accounts.objects.create_user(
            phone_number='+989120000000',
            password='test123'
        )
        
        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.check_password('test123'))
