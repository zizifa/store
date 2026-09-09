# STORE PROJECT — CLINE CORE POLICY

## Role
You are the coding agent for a production-oriented Django ecommerce project. Follow the repository architecture baseline in `docs/architecture/` only when the requested task needs architectural context. Do not read the whole repository by default.

## Stack / architecture
- Django monolith, server-rendered Django Templates (SSR) as the primary frontend.
- JSON/AJAX endpoints only where interaction requires them; do not create a SPA or unnecessary API.
- PostgreSQL is the target production database; Redis/Celery are infrastructure components.
- Passwordless phone OTP authentication.
- ProductVariant-centric catalog/inventory; SKU + barcode are first-class identifiers.
- Inventory is database-authoritative. Use transactions and row locking for reservation/stock changes.
- Payments are provider-abstracted; SnappPay is a provider, not hard-coded into Order models.
- Local hardware uses a local print bridge; never make the cloud backend directly depend on USB/local printer access.

## Context-minimization rule
1. Do NOT scan/read the whole repository unless explicitly required.
2. Start with the exact target file(s), then the nearest dependency files only.
3. Prefer targeted search by symbol/model/view/function over broad codebase search.
4. Do not read generated, dependency, media, build, coverage, cache, database, log, or environment files.
5. Do not read migrations unless the task changes models/migrations or migration history is necessary.
6. Do not read unrelated apps just because they exist.
7. Before reading additional files, explain the dependency reason internally and keep the read set minimal.
8. Never include `.env`, secrets, tokens, private keys, production dumps, or credentials in context, output, logs, commits, or diffs.
9. If a task can be completed from one file, do not inspect five files.
10. After completing a task, report the files actually changed; do not dump unrelated code.

## Change discipline
- Do not rewrite or reformat unrelated code.
- Preserve existing behavior unless the task explicitly changes it or the current behavior is unsafe/incorrect.
- Do not introduce new dependencies without checking whether an existing dependency already solves the problem.
- Do not duplicate business logic between views, templates, and APIs. Put shared business rules in a service/domain layer where appropriate.
- Keep financial and inventory calculations server-authoritative.
- Never trust price, stock, role, payment state, or order state coming from the browser.

## Safety-critical areas
For OTP, authentication, permissions, inventory, checkout, order state transitions, payment callbacks, refunds, and hardware control:
- inspect the smallest relevant dependency chain before changing code;
- add or update tests before declaring success;
- use explicit transactions for atomic state changes;
- ensure retry/idempotency behavior where external calls or asynchronous processing are involved;
- never log secrets, OTP values, payment credentials, or full sensitive customer data.

## Model routing policy
Use the cheapest capable model for the task.
- PRIMARY cheap model: DeepSeek V4 Flash 0731 (or current equivalent low-cost coding model available in OpenRouter).
- COMPLEX coding model: Qwen3 Coder Next (or current equivalent) for multi-file refactors, difficult debugging, concurrency, payments, security, migrations, and architecture.
- Do not use the expensive model for simple CRUD, formatting, small template changes, straightforward tests, or documentation.
- If the cheap model fails twice on the same root problem, escalate instead of repeating expensive context-heavy attempts.
- When escalating, provide only the relevant files and the failure evidence.

## Task workflow
1. Restate the requested outcome in one sentence.
2. Identify the minimum file set.
3. Inspect only that set plus direct dependencies.
4. Plan the smallest safe change.
5. Implement.
6. Run the narrowest relevant tests/checks first.
7. Expand testing only when needed.
8. Update Template/API contract documentation for the feature when applicable.
9. Summarize changed files, tests run, and any remaining risk.

## Git
- Work on a feature/fix branch, never directly on `main`.
- Make small, logically isolated commits.
- Do not reset, rebase, force-push, or delete branches unless explicitly instructed.
