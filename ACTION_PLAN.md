# Robotics LMS — Action Plan

Updated: 2026-11-18, 21:21 EST. Repository pavanjains/lms; main.

## LESSON-01 authored
New apps/lessons staff-only organization library with model/migration, create/edit/archive services and browser pages, title/summary search, kit/grade/status filters and pagination. All active same-organization staff share active lessons; only creator/owner modifies. Archived content retained, visible to creator/owner; no reactivation. Optimistic version check rejects stale writes under organization/lesson locks. LEGO links restricted to HTTPS education.lego.com; no server fetch, copied LEGO content, seed data or suitability/reachability claims.

Essential through Grade 4, Prime Grades 4–8; Grade 4 permits either kit as distinct lesson records, no automatic kit selection. Plain-text instructions rendered escaped. Supporting documents, assignments and student lesson access remain separate increments. Status REVIEW; tests, migration/drift checks NOT RUN here, new CI/browser acceptance PENDING. No runtime database change or feature-flag activation; staff auth gate remains off by default. See docs/LESSON_LIBRARY.md.

## Evidence update
Owner reported CI passed November 18 21:18 after ded6acb. BUG-004 FIXED_VERIFIED and E08-08 CI_PASSED on user report only; run URL/count unavailable, not independently retrieved. Preserve a372751 Ruff F401 one unused ClassInstructor import and ded6acb import-only correction; all tests retained. Prior 21:02 all-CI report through 460d7fa and older evidence retained in linked ledger. New library not covered by prior passes.

[Previous full plan](https://github.com/pavanjains/lms/blob/ded6acb393cb80f20bd3394e6f7c3724ccb40ec7/ACTION_PLAN.md) preserves roadmap/history.

## Next
1. Run library/full CI, migrate locally and verify owner/creator/peer/student boundaries and Grade 4 filters.
2. Supporting-document upload/storage/authorized download controls.
3. Lesson assignments to students/classes with explicit kit/grade checks and version/history decisions.
4. Instructor progress/feedback and student assigned-lesson read-only workspace, reporting.
5. Existing shared-device/browser and creation/reset/login race acceptance; throttling/audit, recovery/session/last-owner, TLS/log redaction/privacy/mail, dependencies/Python 3.14, deployment/restore/training remain release gates.

All implementation/fix commits update this plan, docs/TICKETS.md and docs/IMPLEMENTATION_STATUS.md. No unattended tracking or production authorization.
