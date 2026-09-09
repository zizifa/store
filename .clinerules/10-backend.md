---
paths:
  - "*/models.py"
  - "*/views.py"
  - "*/forms.py"
  - "*/services.py"
  - "*/selectors.py"
  - "*/serializers.py"
  - "*/admin.py"
  - "*/urls.py"
  - "*/tests/**"
  - "shop/**"
---
# Backend rules

- Django business logic must remain server-side.
- Prefer service functions/classes for multi-step business operations instead of large views.
- Keep views thin: validate request, call business logic, build response/context.
- Use `get_object_or_404` where an HTTP 404 is the correct semantic.
- For financial values use integer Rial or the repository's approved Decimal strategy; never FloatField for money.
- For inventory-changing operations use `transaction.atomic()` and the approved locking/reservation strategy.
- For external providers (SMS, payment, shipping) isolate integration code behind a provider/service interface.
- Use `select_related` / `prefetch_related` only when needed to solve demonstrated query patterns; avoid premature optimization.
- Add regression tests for bugs before or with the fix.
