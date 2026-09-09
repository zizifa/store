# Cline Task Prompt Template

Use this template for most tasks.

```text
Goal: <one clear outcome>

Scope:
- Work only on: <exact file/folder>
- First inspect: <exact file(s)>
- Only inspect additional files if a direct dependency requires it.

Do NOT:
- scan the whole repository
- read .env, secrets, databases, media, build output, logs, or dependencies
- modify unrelated files
- introduce new dependencies unless necessary and approved

Implementation:
- Follow the project architecture and applicable .clinerules.
- Keep business logic server-side.
- Preserve existing behavior unless the requested change or a demonstrated bug requires otherwise.

Validation:
- Run only the narrow tests/checks relevant to this task first.
- If they fail, inspect only the files needed to diagnose the failure.

Documentation:
- If the feature changes Template context or an API contract, update its feature contract.

Finish with:
1. files changed
2. tests/checks run
3. remaining risks or follow-up items
```

## Examples

### Small backend fix
```text
Goal: Fix the incorrect cart item delete operation.

Scope:
- Work only on: carts/views.py
- First inspect: carts/views.py
- Read carts/models.py only if needed to confirm the CartItem API.

Do NOT scan the repository.
Do NOT modify unrelated code.

Run the narrow cart test that covers delete/remove behavior.
```

### Template change
```text
Goal: Update the product card layout.

Scope:
- Work only on: templates/store/product_card.html and its directly used stylesheet.
- First inspect the target template and stylesheet.
- Read the target view only if the required context variables are unclear.

Do NOT scan models, migrations, orders, payments, or the whole templates tree.
```

### Critical task
```text
Goal: Fix inventory reservation race condition during checkout.

Scope:
- Start with: inventory/services.py, orders/services.py, inventory/models.py, and the relevant tests.
- Inspect payment code only if the checkout path directly depends on it.

This is a critical domain. Use database transactions/row locking and add a regression concurrency test.
Do NOT change unrelated architecture.
```
