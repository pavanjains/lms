# Implementation Status

Updated: 2026-11-18, 21:21 EST. Evidence: docs/TICKETS.md.

## LESSON-01 authored
Organization-scoped staff lesson library at /staff/lessons/, staff navigation link, initial migration and model/service/UI tests. Title/summary/instructions, HTTPS LEGO Education URL, kit/grade range, archive flag, version/timestamps/creator. All staff see active organization lessons; only creator/owner edit/archive; archived lessons creator/owner only. Model/database grade/kit constraints, escaped text, external link safety, confirmation and CSRF, stale-version conflict checks.

Essential through Grade 4; Prime Grades 4–8; Grade 4 supports either. Pre-K=-1, Kindergarten=0, grades 1–8 numeric for library ranges; student profiles remain their existing string grades. No automatic grade conversion/assignment or kit selection in this slice. External links restricted to education.lego.com over HTTPS; not fetched/imported/verified or seeded.

Tests/migration execution/drift/lint NOT RUN here; new CI/browser/concurrent-edit acceptance PENDING. Source commit creates no runtime data and changes no flags. New migration creates Lesson table only. No uploads/supporting docs, assignment/student lesson access, progress/feedback/reporting. Version is an overwrite guard, not history/audit. Direct ORM writes can bypass semantic clean; services required.

## Verification update/history
Owner November 18 21:18 confirms CI passed after ded6acb: E08-08 CI_PASSED, BUG-004 FIXED_VERIFIED, user-reported only/no run URL/count/not independently retrieved. a372751 Ruff F401 unused ClassInstructor failure preserved; ded6acb import-only correction retains tests. Prior owner 21:02 all-CI report through 460d7fa remains, E08-05 manual/race extensions open. New library not covered by earlier passes.

[Previous full status](https://github.com/pavanjains/lms/blob/ded6acb393cb80f20bd3394e6f7c3724ccb40ec7/docs/IMPLEMENTATION_STATUS.md) preserves account/classroom/credential/sign-in and BUG history. Earlier BUG-002 83 entries/one import error/82 passed/no onboarding methods executed and later owner pass without count remain unchanged. BUG-001/002 owner-verified, BUG-003 full browser acceptance and E05-07 manual session acceptance still open.

## Next / release limits
Supporting document controls, assignment schema/permissions/history, instructor progress/feedback and student read-only lessons/reporting. Existing creation/reset/login concurrency, shared-device/browser/BFCache, throttling/audit/recovery/session/last-owner, TLS/log redaction/privacy/mail/dependency/Python 3.14/deployment/restore/training remain incomplete. Defaults remain off; no production authorization.
