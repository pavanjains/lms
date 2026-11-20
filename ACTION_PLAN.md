# Robotics LMS — Action Plan

Updated: 2026-11-19. Branch: feature/assign-01-instructor-ui.

## ASSIGN-01 instructor UI authored — REVIEW
Class selection from scoped assignment list; lesson/explicit-recipient form; signed, actor/org/class/session-bound 15-minute review; explicit confirmation; scoped snapshot detail/history and POST-only versioned cancellation. Most recent review replaces earlier session review; normal successful confirmation consumes it. All mutations use foundation services and recheck current authority/enrollment/grade/version. No claim of durable exactly-once review-token consumption under concurrent sessions; PostgreSQL/session races remain acceptance work.

Adds HTTP regression tests and library navigation. Student-denial HTTP test uses the student backend with valid session timestamps. No model/migration/settings/password/flag changes, student pages, progress/feedback, document access or student completion controls. Upload flag remains disabled; no real-file activation.

Verification: draft Python syntax/compile checks only during authoring; Django unavailable, tests/Ruff/CI/template rendering/browser/concurrency NOT RUN. UI REVIEW; ASSIGN-01 IN_PROGRESS. No runtime database or credential actions.

## Foundation evidence (supersedes earlier foundation-pending notes)
PR #1 merged at 9012dd194364791dcf5afb569e043936c42b1f04. Both returned checks jobs independently confirmed successful for PR head dddb545, including run 44665321805. Post-merge main run 44665898145 passed per owner, not independently retrieved; no test count inferred. These do not verify this new UI increment or individually establish runtime migration/drift/concurrency/browser coverage. BUG-005 pass after 8e80939 remains user-reported.

## Next
1. Review/commit UI; run targeted HTTP and foundation tests, Ruff and full PostgreSQL CI.
2. Browser acceptance: selection/review/confirm/cancel, stale/revoked access, MFA, CSRF/origins, escaping/cache, and concurrent review/confirmation.
3. Student read-only assignment list/detail with existing session isolation, then instructor-controlled progress/feedback and reporting.

All prior security/operations gates remain: file scanning/parser/request limits, audit/throttling/recovery/session/races/privacy/retention/mail/backups/deployment/training; Python3.14 unverified. No production authorization.

[Complete pre-UI plan/history](https://github.com/pavanjains/lms/blob/9012dd194364791dcf5afb569e043936c42b1f04/ACTION_PLAN.md). Update all three tracking docs with implementation/fix commits.
