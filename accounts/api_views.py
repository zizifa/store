"""JSON API views for passwordless phone OTP customer authentication.

These endpoints are the authoritative server-side authentication surface for
the public customer login flow. All POST endpoints are CSRF protected via the
global CsrfViewMiddleware (no csrf_exempt). The server is authoritative for the
authentication state; no client-side success indication is trusted.
"""
import json

from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from .services.otp import OTPServiceError, send_otp, verify_otp

#: Default authenticated landing destination for customer logins.
DEFAULT_NEXT = 'dashboard'


def _parse_json(request) -> dict:
    """Safely parse the request body as JSON, returning an empty dict on error."""
    if not request.body:
        return {}
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def _get_field(data: dict, request, name: str) -> str:
    """Read a field from JSON body, falling back to POST/GET form data."""
    value = data.get(name) or request.POST.get(name) or request.GET.get(name) or request.POST.get(name)
    return value.strip() if isinstance(value, str) else ''


def _safe_next(request, data=None, default=None) -> str:
    """Resolve a client-provided next URL to a safe local destination URL."""
    if default is None:
        default = reverse('dashboard')
    source = data if isinstance(data, dict) else {}
    next_url = source.get('next') or request.POST.get('next') or request.GET.get('next')
    if (
        isinstance(next_url, str)
        and next_url
        and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()})
    ):
        return next_url
    return default


def _mask_phone(phone) -> str:
    """Return a masked phone number, e.g. +98912*****456. Never reveals full number."""
    from phonenumber_field.phonenumber import PhoneNumber
    s = phone.as_e164 if isinstance(phone, PhoneNumber) else str(phone)
    if len(s) <= 4:
        return s
    return s[:4] + '*' * (len(s) - 7) + s[-3:]


@require_http_methods(["POST"])
def api_otp_request(request):
    """POST /api/v1/auth/otp/request/

    Body: {phone_number, purpose?}
    Success: 200 {"ok": true, "message": "OTP sent"}
    Errors:  400 invalid input, 429 cooldown/rate limit.
    """
    data = _parse_json(request)
    phone = _get_field(data, request, 'phone_number')
    purpose = _get_field(data, request, 'purpose') or 'LOGIN'

    if not phone:
        return JsonResponse({'ok': False, 'message': 'Phone number is required.'}, status=400)

    try:
        from .models import Accounts
        Accounts.objects.normalize_phone(phone)
    except ValidationError:
        return JsonResponse({'ok': False, 'message': 'Please enter a valid phone number.'}, status=400)

    try:
        send_otp(phone, purpose)
    except OTPServiceError as exc:
        return JsonResponse({'ok': False, 'message': str(exc)}, status=429)
    except ValidationError as exc:
        return JsonResponse({'ok': False, 'message': str(exc)}, status=429)

    return JsonResponse({'ok': True, 'message': 'OTP sent'}, status=200)


@require_http_methods(["POST"])
def api_otp_verify(request):
    """POST /api/v1/auth/otp/verify/

    Body: {phone_number, code, purpose?, next?}
    Success: 200 {"ok": true, "message": "Logged in.", "next": <safe next>}
    Errors:  400 invalid input, 401 invalid/expired code.
    """
    data = _parse_json(request)
    phone = _get_field(data, request, 'phone_number')
    code = _get_field(data, request, 'code')
    purpose = _get_field(data, request, 'purpose') or 'LOGIN'

    if not phone or not code:
        return JsonResponse(
            {'ok': False, 'message': 'Phone number and code are required.'}, status=400
        )

    try:
        from .models import Accounts
        Accounts.objects.normalize_phone(phone)
    except ValidationError:
        return JsonResponse({'ok': False, 'message': 'Please enter a valid phone number.'}, status=400)

    try:
        user = verify_otp(phone, purpose, code)
    except ValidationError as exc:
        return JsonResponse({'ok': False, 'message': str(exc)}, status=400)
    except OTPServiceError as exc:
        return JsonResponse({'ok': False, 'message': str(exc)}, status=401)

    # Do not leak whether the OTP was wrong, expired, consumed or locked.
    if user is None or not user.is_active:
        return JsonResponse({'ok': False, 'message': 'Invalid or expired code.'}, status=401)

    auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    next_url = _safe_next(request, data)
    return JsonResponse({'ok': True, 'message': 'Logged in.', 'next': next_url}, status=200)


@require_http_methods(["POST"])
def api_logout(request):
    """POST /api/v1/auth/logout/
    Destroys the server-side session. Returns 401 if there is no session.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'message': 'Not authenticated.'}, status=401)
    auth_logout(request)
    return JsonResponse({'ok': True, 'message': 'Logged out.'}, status=200)


@require_http_methods(["GET"])
def api_me(request):
    """GET /api/v1/auth/me/
    Returns only non-sensitive account information for the current session.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'message': 'Not authenticated.'}, status=401)
    user = request.user
    return JsonResponse({
        'ok': True,
        'user': {
            'id': user.pk,
            'phone_number': _mask_phone(user.phone_number),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        },
    }, status=200)