# Implementation Status

Updated: 2026-11-19. Baseline main92ed0ab; current evidence: TICKETS.md and VALIDATION.json.

## Implemented in source
Stembotic branding; owner bootstrap; gated staff email/MFA, invitations/onboarding/management/deactivation; scoped classroom/membership services/UI; shared student creation/password reset; separately gated student sign-in/session isolation; lesson library and protected staff PDF support; assignment snapshots/services and instructor screens. Foundation PR #1 merged9012dd1; instructor UI/UUID fix PR #2 merged92ed0ab. No production acceptance implied.

Instructor assignment routes are under /staff/lessons/assignments/. Explicit reviewed recipients/version are signed/session-bound with 900s expiry and freshly authorized on confirmation. No automatic roster expansion; snapshots survive lesson changes; retained versioned cancellation permits reassignment. Org UUID string normalization fixed BUG-006. No durable exactly-once session/token consumption under concurrency.

Student home still identity/grade/active class names only. Assigned lesson pages, instructor-controlled progress/status/feedback, reporting and student document authorization remain to build. Student submissions/student-controlled completion excluded.

## Verification
- Foundation pre-merge checks for dddb545 independently retrieved successful, including44665321805.
- Initial UI run44667767312 failed per owner and supplied log:296tests,9errors, UUID JSON serialization; retained as failure history with no inferred passing count.
- BUG-006 ddc000b checks independently retrieved successful in push44668593439 and PR44668981076. BUG-006 FIXED_VERIFIED for reported defect.
- Post-PR1 main run44665898145 passed per owner only; BUG-005 CI after8e80939 user-reported.
- Post-PR2 main92ed0ab CI NOT VERIFIED here. Current full-suite passing count unknown.
- Local JSON reproduction/comparisons were standard-library checks only, not Django runtime execution.
- Real browser/accessibility/shared-device and new assignment/auth/session concurrency acceptance remain PENDING. Source merges did not deploy or execute runtime database migrations.

## Documentation
LOCAL_TESTING.md supplies safe local procedures, not execution evidence; docs/README.md maps all original increment guides to current scope. README/ASSIGNMENTS/DECISIONS/VALIDATION and tracking docs reconciled in doc-only refresh. Procedures were not executed in authoring environment. Future implementation/fix commits must update relevant current docs and retain attributed evidence/failures.

## Release gates
Uploads disabled except controlled synthetic testing: private DB PDF-only,5MiB/file,20active/lesson,100MiB/org incl.archives. Scanning/full parser/CDR/request limits/retention/restore and approved storage architecture remain open. Audit/throttling/recovery/session-policy/TLS/log-redaction/privacy/mail/deployment/backups/training gates, E08-05/BUG-003 and branding/library/document acceptance remain. Python3.14 unverified. No production authorization.

[Full pre-refresh status/history](https://github.com/pavanjains/lms/blob/92ed0ab127149081483c8044ab41cf4e4ee9f82e/docs/IMPLEMENTATION_STATUS.md) preserves previous implementation/failure/evidence links.
