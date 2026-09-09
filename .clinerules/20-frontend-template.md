---
paths:
  - "templates/**"
  - "static/**"
  - "**/*.html"
  - "**/*.css"
  - "**/*.js"
  - "vite.config.*"
---
# Template / frontend rules

- The frontend is Django Template SSR, not a SPA.
- Do not invent context variables. Read the target view/form/API contract first.
- Prefer template inheritance, reusable includes, and small focused partials.
- Keep business rules out of JavaScript when they affect price, stock, payment, permissions, or order state.
- For dynamic interactions, prefer small JSON/AJAX endpoints over introducing a frontend framework unless explicitly requested.
- Avoid inline scripts when CSP compatibility would be affected; prefer static assets and nonce/hash-safe patterns approved by the project.
- Do not load unrelated templates or static bundles just to understand a local change.
- When changing a template contract, update the corresponding feature contract documentation.
