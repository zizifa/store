# Cline Context-Minimization Guide

## Default rule
Cline should read the smallest dependency graph needed to complete the task.

### Examples
- Template bug → target HTML + target view/context only.
- Model bug → target model + directly affected service/test.
- URL bug → target URLconf + target view.
- Cart bug → cart service/view + relevant models + relevant tests; do not read accounts/order unless the code path crosses that boundary.
- Payment bug → payment provider + payment model/service + callback/status tests; do not read the catalog unless the failure is catalog-related.
- CSS issue → target template + target stylesheet; do not inspect backend code unless a missing context variable is suspected.

## Do not broad-scan
Avoid repository-wide scans for:
- "understanding the project"
- generic refactoring
- naming questions
- one-line bugs
- template styling

Broad scans are allowed only for architecture reviews, security audits, migration planning, or cross-app changes.

## Important
`.clineignore` is a safety/context filter, not a substitute for precise prompts. Explicitly referenced files can still be requested by the user, so task prompts should always specify the intended scope. Cline currently documents `.clineignore` as the project-level mechanism for excluding files from context. Use it together with targeted prompts. 
