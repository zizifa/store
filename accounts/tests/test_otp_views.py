"""Focused tests for the Part 2 customer OTP web flow (views, session login).

Covers only the critical customer-facing behaviours: OTP request/verify,
customer creation, existing-customer login, logout, dashboard protection,
safe ``next`` handling, and preservation of admin/staff password login.
"""
import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import OTPChallenge

User = get_user_model()


class FakeProvider:
    """Captures OTP codes passed through the SMS provider (dev proxy)."""

    def __init__(self):
        self.codes = {}

    def send_otp(self, phone, code):
        self.codes[phone] = code


def _json(data):
    return json.dumps(data)


@override_settings(
    OTP_TTL_SECONDS=120,
    OTP_MAX_ATTEMPTS=5,
    OTP_RESEND_COOLDOWN_SECONDS=60,
    OTP_LENGTH=6,
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
)
class CustomerOTPWebFlowTest(TestCase):
    def setUp(self):
        self.provider = FakeProvider()
        self.patcher = patch(
            'accounts.services.otp.get_sms_provider', return_value=self.provider
        )
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.client = Client()
        self.phone = '+989120000000'
        self.alt_phone = '+989120000001'

    # ---- helpers ----
    def _request_otp(self, phone=None):
        return self.client.post(
            reverse('api_otp_request'),
            data=_json({'phone_number': phone or self.phone}),
            content_type='application/json',
        )

    def _verify(self, phone, code, **extra):
        payload = {'phone_number': phone, 'code': code, 'purpose': 'LOGIN'}
        payload.update(extra)
        return self.client.post(
            reverse('api_otp_verify'),
            data=_json(payload),
            content_type='application/json',
        )

    def _request_and_code(self, phone=None):
        phone = phone or self.phone
        self._request_otp(phone)
        code = self.provider.codes.get(phone)
        self.assertIsNotNone(code, 'OTP code should have been captured by provider')
        return code

    def _login(self, phone=None):
        phone = phone or self.phone
        code = self._request_and_code(phone)
        return self._verify(phone, code)

    # ---- 1. request + 2. invalid phone ----
    def test_otp_request_success(self):
        resp = self._request_otp()
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body['ok'])
        self.assertEqual(body['message'], 'OTP sent')
        self.assertNotIn('code', resp.content.decode())

    def test_invalid_phone_returns_validation_error(self):
        resp = self.client.post(
            reverse('api_otp_request'),
            data=_json({'phone_number': 'not-a-phone'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.json()['ok'])

    # ---- 3. correct OTP logs in + 4. wrong OTP fails ----
    def test_correct_otp_logs_customer_in(self):
        code = self._request_and_code()
        resp = self._verify(self.phone, code)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['ok'])
        self.assertIn('_auth_user_id', self.client.session)

    def test_wrong_otp_fails(self):
        self._request_otp()
        resp = self._verify(self.phone, '000000')
        self.assertEqual(resp.status_code, 401)
        self.assertFalse(resp.json()['ok'])
        # Session must not be established.
        self.assertNotIn('_auth_user_id', self.client.session)

    # ---- 5. new customer + 6. existing customer ----
    def test_new_customer_created_on_verify(self):
        self.assertFalse(User.objects.filter(phone_number=self.phone).exists())
        code = self._request_and_code()
        resp = self._verify(self.phone, code)
        self.assertEqual(resp.status_code, 200)
        user = User.objects.get(phone_number=self.phone)
        self.assertFalse(user.has_usable_password())
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_existing_customer_logs_in(self):
        User.objects.create_user(phone_number=self.phone)
        self.assertEqual(User.objects.filter(phone_number=self.phone).count(), 1)
        code = self._request_and_code()
        resp = self._verify(self.phone, code)
        self.assertEqual(resp.status_code, 200)
        # No duplicate account created.
        self.assertEqual(User.objects.filter(phone_number=self.phone).count(), 1)

    # ---- 7. logout ----
    def test_logout_destroys_session(self):
        self._login()
        self.assertIn('_auth_user_id', self.client.session)
        resp = self.client.post(reverse('api_logout'))
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.get(reverse('api_me')).status_code, 401)

    # ---- 8. dashboard requires auth ----
    def test_dashboard_requires_authentication(self):
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith(reverse('login')))

    def test_dashboard_accessible_after_login(self):
        self._login()
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)

    # ---- 9. unsafe next + 10. safe next ----
    def test_unsafe_next_url_rejected(self):
        code = self._request_and_code()
        resp = self._verify(self.phone, code, next='https://evil.example.com/phish')
        self.assertEqual(resp.status_code, 200)
        # Open redirect rejected: falls back to the dashboard.
        self.assertEqual(resp.json()['next'], reverse('dashboard'))

    def test_safe_next_url_used(self):
        code = self._request_and_code()
        resp = self._verify(self.phone, code, next='/accounts/my-orders/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['next'], '/accounts/my-orders/')

    # ---- 11. admin/staff password login preserved ----
    def test_staff_password_login_still_works(self):
        staff = User.objects.create_superuser(
            phone_number=self.alt_phone, password='VerySecure123'
        )
        ok = self.client.login(phone_number=self.alt_phone, password='VerySecure123')
        self.assertTrue(ok)
        self.assertEqual(
            self.client.session['_auth_user_id'], str(staff.pk)
        )

    def test_otp_never_stored_plaintext(self):
        code = self._request_and_code()
        challenge = OTPChallenge.objects.latest('id')
        self.assertNotEqual(challenge.code_hash, code)
        self.assertNotIn(code, str(challenge.code_hash))


class CustomerCanonicalRoutesTest(TestCase):
    """Server-rendered pages for the customer web flow."""

    def test_login_page_renders(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)

    def test_legacy_customer_password_routes_disabled(self):
        # Registration/forgot/reset are now redirected to passwordless login.
        self.assertEqual(self.client.get(reverse('register')).status_code, 302)
        self.assertEqual(self.client.get(reverse('forgotpassword')).status_code, 302)