# Robotics LMS — Action Plan

Updated: 2026-11-19. Repository pavanjains/lms; feature/assign-01-foundation.

## ASSIGN-01 foundation: REVIEW; feature IN_PROGRESS
Adds LessonAssignment model, migration 0002, transactional creation/cancellation, scoped query services and 34 authored regression test methods. Individual explicit recipients receive lesson-field/version snapshots. Fresh staff/MFA, current class authority, active enrollment/account/org and grade/kit checks required; Grade 4 either kit, Pre-K/K mapping. Batch all-or-nothing; one active class/student/lesson; cancellation retains history and permits reassignment. Later enrollment never silently expands assignments.

No routes/templates/settings/flags changed, no submissions/student completion/progress/feedback/document access added. Main unchanged by this feature-branch commit. No runtime database/credential actions or migration execution. Direct ORM authorization/snapshot immutability is not database-enforced; services are the supported write path.

Draft syntax and migration/model field-name checks were performed during authoring, not Django runtime verification. Django unavailable: tests, Ruff, migration/drift, full PostgreSQL CI and concurrency/browser acceptance NOT RUN. The 34 figure counts authored methods, not passing tests.

## Evidence
Owner reported CI passed after 8e80939 on 2026-11-18; user-reported only, run URL/count unknown, not independently retrieved. BUG-005 FIXED_VERIFIED on that evidence. Does not cover ASSIGN-01 or establish migration/browser/security/restore acceptance.

## Next
1. Run targeted tests, full PostgreSQL CI, migration/drift and concurrency checks on foundation.
2. Instructor selection/review/confirm/list/detail and POST-only cancellation; explicit reviewed recipients and expected lesson version.
3. Student read-only list/detail using existing student session/route/cache guards; A/B isolation, CSRF/origin/method/escaping/cache and revoked-access acceptance.
4. Instructor-controlled progress/feedback, then reporting. Document access requires separate assignment-aware authorization and safety work.

BRAND-01/DOC-01/LESSON-01 retain outstanding acceptance. Upload flag remains false; synthetic testing only. PDF limits 5 MiB/file,20 active/lesson,100 MiB/org including archives; private DB storage, no public URLs. Signature/integrity checks are not malware scanning/full parsing. Audit/throttling/recovery/session/races/privacy/retention/mail/backups/deployment/training gates remain; Python3.14 unverified. No production authorization.

[Complete pre-assignment plan](https://github.com/pavanjains/lms/blob/8e80939a606f5e967451c811cf178ca85bc422db/ACTION_PLAN.md) preserves prior roadmap/history/evidence links. Update this plan, docs/TICKETS.md and docs/IMPLEMENTATION_STATUS.md with implementation/fix commits.
