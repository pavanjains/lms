# Robotics LMS — Action Plan

Updated: 2026-11-18, 21:44 EST. Repository pavanjains/lms; main.

## Current BUG-005 correction
Restore NumericPasswordValidator accidentally omitted from base AUTH_PASSWORD_VALIDATORS in 5032dc4. Preserve original similarity, minimum-length and common-password validators and order. New SimpleTestCase regressions inspect actual configured list without overriding it, require numeric-specific rejection of a long digit-only password, retain short/common checks and accept a strong synthetic nonnumeric password. Correction/tests authored, NOT RUN here; CI PENDING, status REVIEW. No existing password/account/session modification, migration, dependency or flag changes. Restoration is prospective validation, not retroactive credential review.

## BRAND-01 / DOC-01 authored
Stembotic header/title in shared base including MFA; production 400/403/404/500 and generic CSRF pages branded. Health JSON/download payloads/framework debug pages are not HTML branding surfaces.

Protected PDF lesson documents: database BLOB storage, 5 MiB/file, 20 active/lesson, 100 MiB/org including archives. Creator/owner upload/archive, authorized library staff download as attachment; no public media URL, student document route, automatic scanning or assignment. Signature/end-marker checks are not malware scanning or full PDF validation. New documents flag remains false by default; local synthetic tests only. Content/quota/parent version changes atomic. See docs/LESSON_DOCUMENTS.md.

Status REVIEW; tests, migration/drift, CI/browser/storage/restore acceptance PENDING. No runtime files/database modified here, no feature activation. Migration adds LessonDocument table; no dependency changes. LESSON-01 aa3d0d9 CI still unreported.

[Previous plan](https://github.com/pavanjains/lms/blob/aa3d0d9ecf1049c15c411550058687b7b9ce471b/ACTION_PLAN.md) preserves roadmap/history. Owner 21:18 pass after ded6acb remains user-reported only/count unknown/not independently retrieved; E08-08 CI_PASSED, BUG-004 FIXED_VERIFIED, earlier failure retained. New library/doc changes not covered.

## Next
1. Run password-policy regression/full PostgreSQL CI after BUG-005; do not mark verified before actual evidence.
2. Full PostgreSQL CI, migrate locally, verify Stembotic pages and synthetic upload/download/archive/org/student boundaries.
3. Real-file scanning/CDR decision, parser validation and server request-size/rate limits before real uploads; database growth/backup/restore review.
4. Assignments with grade/kit/version/document authorization, then progress/feedback/student read-only lessons/reporting.
5. Existing shared-device/browser/races, audit/throttling/recovery/session/last-owner, TLS/log-redaction/privacy/mail/dependency/Python 3.14/deployment/training gates remain.

Update this plan, docs/TICKETS.md and docs/IMPLEMENTATION_STATUS.md per implementation/fix. No launch authorization or unattended work.
