"""Tests for the passwordless OTP customer authentication JSON API."""
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
class OTPApiTestCase(TestCase):
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
    def _request_otp(self, phone=None, **extra):
        return self.client.post(
            reverse('api_otp_request'),
            data=_json({'phone_number': phone or self.phone}),
            content_type='application/json',
            **extra,
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


class OTPRequestEndpointTests(OTPApiTestCase):
    def test_otp_request_success(self):
        resp = self._request_otp()
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body['ok'])
        self.assertEqual(body['message'], 'OTP sent')

    def test_otp_request_invalid_phone(self):
        resp = self.client.post(
            reverse('api_otp_request'),
            data=_json({'phone_number': 'not-a-phone'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.json()['ok'])

    def test_otp_request_missing_phone(self):
        resp = self.client.post(
            reverse('api_otp_request'), data=_json({}), content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

    def test_otp_request_does_not_return_plaintext_code(self):
        resp = self._request_otp()
        self.assertNotIn('code', resp.content.decode())
        self.assertNotIn('otp', resp.json())

    def test_otp_request_rate_limit_returns_429(self):
        # First request ok; immediate second should hit cooldown (~60s).
        self._request_otp()
        resp = self._request_otp()
        self.assertEqual(resp.status_code, 429)


class OTPVerifyEndpointTests(OTPApiTestCase):
    def test_otp_verify_success_and_session(self):
        code = self._request_and_code()
        resp = self._verify(self.phone, code)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body['ok'])
        self.assertEqual(body['next'], reverse('dashboard'))
        # Session is authenticated server-side.
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.session['_auth_user_id'], str(User.objects.get(phone_number=self.phone).pk))

    def test_otp_verify_wrong_code(self):
        self._request_otp()
        resp = self._verify(self.phone, '000000')
        self.assertEqual(resp.status_code, 401)
        self.assertFalse(resp.json()['ok'])

    def test_otp_verify_expired(self):
        code = self._request_and_code()
        challenge = OTPChallenge.objects.latest('id')
        from django.utils import timezone
        from datetime import timedelta
        challenge.expires_at = timezone.now() - timedelta(minutes=10)
        challenge.save()
        resp = self._verify(self.phone, code)
        self.assertEqual(resp.status_code, 401)

    def test_otp_verify_reuse_rejected(self):
        code = self._request_and_code()
        self._verify(self.phone, code)
        resp = self._verify(self.phone, code)
        self.assertEqual(resp.status_code, 401)

    def test_otp_verify_new_customer_created_and_logged_in(self):
        code = self._request_and_code()
        resp = self._verify(self.phone, code)
        self.assertEqual(resp.status_code, 200)
        user = User.objects.get(phone_number=self.phone)
        self.assertFalse(user.has_usable_password())

    def test_otp_verify_existing_customer_login(self):
        user = User.objects.create_user(phone_number=self.phone)
        user.first_name = 'Sara'
        user.save()
        code = self._request_and_code()
        resp = self._verify(self.phone, code)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.filter(phone_number=self.phone).count(), 1)
        self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))

    def test_otp_verify_missing_code_400(self):
        self._request_otp()
        resp = self.client.post(
            reverse('api_otp_verify'),
            data=_json({'phone_number': self.phone}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_safe_next_url_works(self):
        code = self._request_and_code()
        resp = self._verify(self.phone, code, next='/accounts/dashboard/')
        self.assertTrue(resp.json()['ok'])
        self.assertEqual(resp.json()['next'], '/accounts/dashboard/')

    def test_unsafe_next_url_rejected(self):
        code = self._request_and_code()
        resp = self._verify(self.phone, code, next='https://evil.example.com/phish')
        self.assertTrue(resp.json()['ok'])
        # Falls back to safe default destination.
        self.assertEqual(resp.json()['next'], reverse('dashboard'))


class OTPMeLogoutTests(OTPApiTestCase):
    def _login(self, phone=None):
        phone = phone or self.phone
        code = self._request_and_code(phone)
        self._verify(phone, code)

    def test_me_requires_auth(self):
        resp = self.client.get(reverse('api_me'))
        self.assertEqual(resp.status_code, 401)

    def test_me_returns_masked_phone_only(self):
        self._login()
        resp = self.client.get(reverse('api_me'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['user']
        self.assertIn('*', data['phone_number'])
        self.assertNotIn(self.phone, data['phone_number']
                         .replace('*', '') if '*' in data['phone_number'] else '')
        self.assertNotIn('password', resp.content.decode().lower())
        self.assertNotIn('code_hash', resp.json()['user'])

    def test_logout_requires_auth(self):
        resp = self.client.post(reverse('api_logout'))
        self.assertEqual(resp.status_code, 401)

    def test_logout_clears_session(self):
        self._login()
        self.assertIn('_auth_user_id', self.client.session)
        resp = self.client.post(reverse('api_logout'))
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        # me should now be 401
        self.assertEqual(self.client.get(reverse('api_me')).status_code, 401)


class OTPDashboardTests(OTPApiTestCase):
    def test_authenticated_dashboard_access(self):
        code = self._request_and_code()
        self._verify(self.phone, code)
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_unauthenticated_dashboard_redirect(self):
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith(reverse('login')))


class OTPCSRFStaffTests(OTPApiTestCase):
    def test_csrf_enforced_for_json_post(self):
        csrf_client = Client(enforce_csrf_checks=True)
        resp = csrf_client.post(
            reverse('api_otp_request'),
            data=_json({'phone_number': self.phone}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 403)

    def test_csrf_enforced_for_logout(self):
        csrf_client = Client(enforce_csrf_checks=True)
        resp = csrf_client.post(reverse('api_logout'))
        self.assertEqual(resp.status_code, 403)

    def test_customer_password_remains_unusable(self):
        code = self._request_and_code()
        self._verify(self.phone, code)
        user = User.objects.get(phone_number=self.phone)
        self.assertFalse(user.has_usable_password())

    def test_staff_password_login_still_works(self):
        staff = User.objects.create_superuser(
            phone_number=self.alt_phone, password='VerySecure123'
        )
        ok = self.client.login(phone_number=self.alt_phone, password='VerySecure123')
        self.assertTrue(ok)
        self.assertEqual(
            self.client.session['_auth_user_id'], str(staff.pk)
        )

    def test_plaintext_otp_not_stored_in_db(self):
        code = self._request_and_code()
        challenge = OTPChallenge.objects.latest('id')
        self.assertNotEqual(challenge.code_hash, code)
        self.assertNotIn(code, str(challenge.code_hash))
