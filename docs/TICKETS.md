# Development Tickets and Fix Ledger

Updated: 2026-11-19.

## ASSIGN-01 — IN_PROGRESS; instructor UI REVIEW
Authored scoped list/class selection, lesson/recipient selection, read-only review, explicit confirmation, assignment snapshot detail/history and POST-only cancellation. Signed review binds actor/org/class, lesson version and exact student IDs; session token equality and 15-minute expiry required. Normal success consumes review; newer review replaces it. Confirmation ignores unreviewed posted recipient/lesson fields and calls transactional foundation services for fresh authorization/compatibility/version checks. No durable exactly-once nonce store; concurrent session/replay races remain unverified.

14 HTTP regression methods authored for no writes before confirmation, checkbox/token/session/actor/expiry/replacement controls, stale lessons and enrollment/membership revocation, forged recipients/org access, cache/referrer/escaping, cancellation/method/version requirements, MFA/student/anonymous/flag denial and CSRF/origin checks. Student-denial test uses student backend and valid session timestamps, not anonymous fallback. Draft syntax/compile only; Django tests/Ruff/templates/CI/browser/PostgreSQL concurrency NOT RUN. Not marked complete or FIXED_VERIFIED; 14 is authored methods, not passing tests.

No changes to models/migrations/settings/password validators/flags, student routes, documents, submissions, progress/feedback or student completion. No runtime migration/data/credential changes. Uploads remain disabled.

## ASSIGN-01 foundation evidence
PR #1 merged at 9012dd1, preserving dddb545 and 34 authored foundation test methods. Two returned checks jobs independently confirmed successful before merge, including run 44665321805. Owner reported post-merge main run 44665898145 passed; not independently retrieved, count unknown. Supersedes historical foundation branch-only/CI-pending notes, not UI verification or individually proven migration/drift/concurrency/browser acceptance.

## Carry-forward
BUG-005 FIXED_VERIFIED per owner CI after 8e80939, not independently retrieved. Existing E08-08 CI_PASSED/BUG-004 FIXED_VERIFIED attribution retained; E08-05 IN_PROGRESS/BUG-003 REVIEW and BRAND-01/DOC-01/LESSON-01 acceptance remain open. File safety/student document authorization, shared-device/browser/races/audit/throttling/recovery/session/privacy/retention/backups/deployment gates remain.

[Complete pre-UI ledger](https://github.com/pavanjains/lms/blob/9012dd194364791dcf5afb569e043936c42b1f04/docs/TICKETS.md) preserves earlier evidence/failures/counts/statuses and history links. No test counts inferred from successful jobs.
