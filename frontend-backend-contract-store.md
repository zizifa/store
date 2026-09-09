قرارداد همکاری Frontend و Backend — Store

نسخه: 1.0 — 2026-09-08
معماری: Django Server-Rendered Templates + API محدود و نسخه‌بندی‌شده

1) تصمیم معماری

Frontend اصلی با Django Templates است؛ پروژه SPA نیست.

API فقط برای AJAX/JSON و Integrationهای لازم استفاده می‌شود.

Backend منبع حقیقت قیمت، موجودی، تخفیف، Order و Payment است.

فعلاً همه‌چیز Local-first است؛ Deployment بعداً.

Django Admin برای مدیریت فنی می‌ماند؛ Staff Dashboard برای عملیات روزمره.

2) مرزبندی

Backend

Model، ORM، Business Logic، Services، Views، URL names، Validation، Auth، Inventory، Payment، API contracts.

Frontend

HTML، CSS، JS، Responsive، Accessibility، Template rendering، نمایش خطا، مصرف Context/API.

Frontend نباید منطق قیمت/موجودی/پرداخت/دسترسی را به‌عنوان منبع حقیقت اجرا کند.

3) Template Contract

نام‌گذاری پیشنهادی:

templates/
  base.html
  includes/
  catalog/
  cart/
  checkout/
  accounts/
  inventory/

برای URLها از {% url %} و برای static از {% static %} استفاده شود.

قبل از شروع هر Template، Backend باید Context Contract را ثبت کند: نام کلید + نوع داده + معنی + optional بودن.

4) API Contract

APIها با الگوی زیر:

/api/v1/<domain>/<resource>/

موفق:

{
  "success": true,
  "data": {},
  "error": null
}

خطا:

{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_QUANTITY",
    "message": "تعداد واردشده معتبر نیست.",
    "field_errors": {}
  }
}

Statusهای اصلی: 200, 201, 400, 401, 403, 404, 409, 422, 429, 500.

هر endpoint باید Method/URL/Auth/CSRF/Request/Response/Errors/Idempotency/Permissions را مستند کند.

5) Auth/OTP

Phone → Request OTP → Verify OTP → Django login() → Session Cookie → request.user

OTP در localStorage ذخیره نشود.

برای تغییر وضعیت از CSRF استفاده شود.

UI برای cooldown، expiry، invalid و rate limit state داشته باشد.

6) Cart/Checkout

Frontend فقط ورودی‌هایی مثل quantity و variant را ارسال می‌کند.
Backend قیمت نهایی، تخفیف، موجودی، Payment و Order را تعیین می‌کند.

7) Inventory / Scanner / Printing

Scanner

Datalogic QD2300 را به‌عنوان Keyboard/HID input می‌گیریم. مسیر منطقی:

Scanner → focused input → POST /api/v1/inventory/scan/ → Variant → UI

Printing

MEVA TP-UNW برای فیش/چاپ حرارتی در نظر گرفته می‌شود. برای Label Printer چسبی دستگاه مستقل لازم است. Frontend نباید به مدل printer قفل شود.

UI → Print Job Contract → Local Print Bridge → Printer

8) Git Workflow

main
  ├── feature/<domain>-<name>
  ├── fix/<domain>-<issue>
  └── refactor/<domain>-<name>

Push مستقیم به main ممنوع.

هر Feature با PR وارد main می‌شود.

Context/API breaking changes باید قبل از Merge اعلام شوند.

9) Feature Contract Template

Feature:
Owner Backend:
Owner Frontend:
Template URL:
Template file:
Django URL name:
View/Service:
Context keys:
Forms:
API Method + URL:
Request schema:
Response schema:
Error codes:
Auth:
Permissions:
Loading state:
Empty state:
Error state:
Done criteria:

10) Definition of Done

UI مطابق طراحی و RTL

Context/API contract رعایت شده

Loading/Empty/Error/403/404/409/429/500 state مشخص

Responsive بررسی شده

Accessibility پایه رعایت شده

بدون secret

Console error بی‌دلیل وجود ندارد

PR قابل Review است

11) مالکیت فایل‌ها

مسیر

مالک اصلی

templates/

Frontend

static/

Frontend

models.py, services.py

Backend

views.py, urls.py

Backend

forms.py

Backend

docs/frontend-contract/

مشترک