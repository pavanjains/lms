# Implementation Status

Updated: 2026-11-19. Evidence: docs/TICKETS.md.

## ASSIGN-01 foundation authored; feature IN_PROGRESS
LessonAssignment model/migration, transactional create/cancel services, scoped read queries and latest 34-method regression module added on feature/assign-01-foundation. Original Lesson implementation, password validators, middleware, settings, routes and feature flags unchanged.

Explicit students receive individual lesson-field/version snapshots. Fresh verified staff/current class authority, active org/class/account/enrollment/profile and grade/kit checks; Grade4 either kit and Pre-K/K mapping supported. Reviewed version guards stale lesson selection. Whole batch succeeds or rolls back, including simulated second-insert failure test. No silent roster expansion. One active class/student/lesson; cancellation keeps actor/time/version history and permits reassignment.

Student query results require current active account/org/class/enrollment and enabled student auth, exclude cancelled work and isolate identity. Staff queries follow current classroom authority. Lesson edits/archive leave valid assigned snapshots intact. Direct ORM authorization/snapshot immutability not DB-enforced; supported writes go through services.

No HTTP/UI, downloads, submissions, student completion, progress or feedback in foundation. Instructor review/confirm/list/detail/cancel and student read-only pages next, with session/CSRF/origin/escaping/cache/browser and PostgreSQL concurrency checks.

## Verification
Draft Python syntax and migration/model field-name comparison performed during authoring only; no Django runtime/drift verification. Django unavailable: 34 authored test methods NOT EXECUTED, Ruff NOT RUN, migration/drift/full PostgreSQL CI/concurrency/browser acceptance PENDING. No migration or runtime credential/data changes executed; foundation REVIEW, not production-ready or end-to-end complete.

BUG-005 FIXED_VERIFIED per owner's 2026-11-18 CI-passed report after 8e80939, not independently retrieved/run URL/count unknown. Does not cover ASSIGN-01. No new passing counts inferred.

## Carry-forward
Stembotic branding/private lesson PDFs remain present; BRAND-01/DOC-01/LESSON-01 retain outstanding acceptance. Uploads remain disabled except controlled synthetic testing; signature/integrity checks are not malware scanning/full PDF validation. Student document authorization, parser/scanning/request limits/storage restore/audit/throttling/recovery/session/races/browser/privacy/retention/mail/deployment/training remain release gates. Python3.14 support unverified. No production authorization.

[Full pre-assignment status](https://github.com/pavanjains/lms/blob/8e80939a606f5e967451c811cf178ca85bc422db/docs/IMPLEMENTATION_STATUS.md) preserves prior implementation/BUG history and earlier evidence links. No earlier failure or user-reported attribution is converted into independent verification.
