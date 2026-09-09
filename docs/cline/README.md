# Store — Cline Configuration Pack

The Cline configuration pack lives inside the repository so the workspace rules
apply automatically.

## Files
- `.clinerules/00-store-core.md` — always-on project policy and cost controls.
- `.clinerules/10-backend.md` — conditional backend rules.
- `.clinerules/20-frontend-template.md` — conditional Template/asset rules.
- `.clinerules/30-critical-domains.md` — conditional security/transaction rules.
- `.clineignore` — files and directories Cline should not load by default.
- `docs/cline/model-routing-policy.md` — model selection/cost policy.
- `docs/cline/context-minimization.md` — practical rules for keeping context small.
- `docs/cline/task-prompt-template.md` — suggested task prompt pattern.

## Placement

The managing agent keeps the `.clinerules/` directory and `.clineignore` at the
repository root so workspace rules apply automatically.

## Important

Keep `.env`, database files, media uploads, build output, logs, and other
generated artifacts out of model context. Keep the ignore list under version
control, but never commit actual secrets.
