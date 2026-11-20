# Development Tickets and Fix Ledger

Updated: 2026-11-19.

## BUG-006 — UUID organization cannot serialize in assignment review
Status REVIEW; correction/tests authored, rerun PENDING. Introduced in UI f52a592. Owner-reported failed run 44667767312; supplied paste.txt read directly: Ran 296 tests in 12.766s, FAILED (errors=9), system checks no issues. Nine reported errors share UUID JSON serialization failure at assignment_create signing.dumps. No inferred passing count, independent Actions-log retrieval or new pass claim.

Organization.id is UUIDField. Fix only two runtime expressions: payload org uses str(user.organization_id), and confirmation compares against str(user.organization_id). Avoid UUID-to-string mismatch after deserialization; keep default JSON signing, all other IDs, HMAC/expiry/session/actor/class/authority checks and service contracts. No schema/settings/password/feature-flag change.

Two dedicated regressions authored using a real UUID organization: review token JSON round-trip and successful confirmation; correctly signed wrong-org token denied even when session token matches. Existing 14 UI and 34 foundation methods retained, not removed or weakened. Standard-library reproduction confirmed original TypeError and normalized JSON comparisons only. Django tests/Ruff/full PostgreSQL CI/browser/concurrency NOT RUN for correction; not FIXED_VERIFIED.

## ASSIGN-01 — IN_PROGRESS; instructor UI REVIEW
Scoped selection/review/confirmation/history/detail/POST-only cancellation authored. Exact reviewed recipients/version bound to actor/org/class/session with 15-minute expiry and current service authorization checks. No durable exactly-once nonce store; session/replay races unverified. Student screens/progress/feedback/document access/completion controls not delivered. No runtime data/migration/credential actions; uploads disabled.

Foundation merged PR #1 at 9012dd1 preserving dddb545. Both returned checks jobs independently confirmed successful, including run 44665321805. Post-merge run 44665898145 passed per owner, not independently retrieved/count unknown. Earlier foundation evidence does not establish UI fix verification.

## Carry-forward
BUG-005 FIXED_VERIFIED per owner CI after 8e80939; E08-08/BUG-004 attribution retained. E08-05 IN_PROGRESS, BUG-003 REVIEW, BRAND-01/DOC-01/LESSON-01 acceptance and file safety/shared-device/browser/races/audit/throttling/recovery/session/privacy/retention/backups/deployment gates remain open.

[Complete pre-fix ledger](https://github.com/pavanjains/lms/blob/f52a5928f697f6f13b283e1fa74a157710bd2e64/docs/TICKETS.md) preserves prior statuses, evidence/failures/counts and history links.
