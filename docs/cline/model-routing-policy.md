# Cline Model Routing Policy

## Goal
Minimize cost while keeping task success high.

## Default routing
| Task | Model tier |
|---|---|
| Small bug fix, one-file edit, simple CRUD | Cheap coding model |
| Template/CSS/JS adjustment | Cheap coding model |
| Simple tests or documentation | Cheap coding model |
| Multi-file feature in one app | Cheap coding model first; escalate only if blocked |
| Large refactor across apps | Complex coding model |
| Authentication / OTP security | Complex coding model |
| Payment / SnappPay | Complex coding model |
| Inventory locking / race conditions | Complex coding model |
| Data migration / legacy migration | Complex coding model |
| Security review / production incident | Complex coding model |
| Architecture change | Complex coding model |

## Cost controls
1. Do not ask Cline to "understand the whole project" for a local task.
2. Give the exact target path(s) in the task prompt whenever possible.
3. Ask for a targeted symbol search before broad search.
4. Escalate only after concrete evidence that the cheaper model is blocked.
5. When escalating, include the previous model's failure summary instead of replaying the whole conversation context.
6. Never include `.env`, databases, media, build artifacts, or large data files.
7. Prefer incremental tasks and commits over one giant refactor request.

## Suggested task prompt pattern
"Work only on <target>. First inspect <file1> and, only if necessary, <file2>. Do not scan the repository. Implement <goal>. Run <narrow test>. Do not modify unrelated files. Update the feature contract if the Template/API contract changes."
