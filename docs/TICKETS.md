# Development Tickets and Fix Ledger

Updated: 2026-11-19.

## ASSIGN-01 — IN_PROGRESS; foundation REVIEW
Model/migration/services and latest 34-method regression module authored. Explicit students get original lesson FK/version plus title, summary, URL, instructions, kit and grade-range snapshots. Organization-first mutations reuse existing fresh staff/MFA and class authorization. Active same-org recipients/enrollment/profiles, kit/grade range and reviewed lesson version checked before atomic writes. Empty/duplicate/malformed recipients, stale/archived lesson or incompatible/unauthorized batch rejected. Conditional DB uniqueness prevents duplicate active class/student/lesson; cancellation actor/time pair and positive-version constraints included.

Scoped staff/student queries recheck current authority/account/org/class/enrollment. Library edits/archive do not rewrite assigned content. Cancellation retains actor/time/version, permits reassignment; archived-class cancellation owner-only. No snapshot editing/student mutation service; raw ORM bypass is not an approved write path and DB does not enforce cross-table authorization/immutability.

Regression methods cover all copied fields, explicit roster behavior, Grade4 either kit, Pre-K/K mapping, stale reviews, authorization, account/MFA/membership revocation, second-insert rollback, database constraints, cancellation/retries/reassignment, shared students and read isolation. 34 authored methods, NOT a passing count. Prior draft syntax/field-name checks only; Django tests/Ruff/migration/drift/PostgreSQL concurrency/browser checks NOT RUN; CI PENDING.

Remaining: instructor/student HTTP/UI, session backend integration and CSRF/origin/method/escaping/cache/browser A/B acceptance. No new routes/settings/flags, submissions, completion controls, progress/feedback or document authorization in foundation. Feature branch only; no runtime migration/data/credential changes.

## BUG-005 — FIXED_VERIFIED, user-reported CI
Owner reported CI passed after 8e80939 on 2026-11-18; not independently retrieved, URL/count unknown. NumericPasswordValidator restored after accidental omission in 5032dc4; other validators retained. No existing passwords/accounts/sessions changed or weak-account creation reported. Earlier pending notes describe authoring time; latest report does not cover ASSIGN-01.

## Carry-forward
BRAND-01/DOC-01/LESSON-01 retain migration/browser/security/operations acceptance. PDFs disabled by default; 5 MiB/file,20 active/lesson,100 MiB/org including archives, private DB storage/staff attachment downloads. No antivirus/CDR/full parser/student file authorization. Existing shared-device/races/audit/throttling/recovery/session/privacy/retention/backups/deployment gates open.

[Complete pre-assignment ledger](https://github.com/pavanjains/lms/blob/8e80939a606f5e967451c811cf178ca85bc422db/docs/TICKETS.md) preserves E01-E22/E08 and BUG history, earlier failures/counts and user-reported evidence. Unaffected statuses unchanged, including E08-08 CI_PASSED/BUG-004 FIXED_VERIFIED user-reported, E08-05 IN_PROGRESS and BUG-003 REVIEW. No fabricated counts or independent Actions claims.
