---
paths:
  - "accounts/**"
  - "cart/**"
  - "carts/**"
  - "orders/**"
  - "order/**"
  - "payments/**"
  - "inventory/**"
  - "notifications/**"
---
# Critical domain rules

For authentication, OTP, cart merge, checkout, inventory, order, payment, refund, shipping, and notification code:

- Treat the database as the source of truth for financial and stock state.
- Make state transitions explicit and validate allowed transitions.
- Make external callbacks/retries idempotent.
- Do not hold a database transaction open while waiting on an external network call.
- For inventory reservations and final stock changes, lock the relevant rows and keep the local mutation atomic.
- Separate `Reservation`, `SALE_OUT`, `CANCELLATION_IN`, and `RETURN_IN` semantics.
- Never mark a payment paid merely because a browser returned from a payment page.
- Never trust client-side totals; recompute authoritative totals server-side.
- Do not log OTP codes, payment secrets, authentication tokens, or sensitive personal data.
