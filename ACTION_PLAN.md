# Robotics LMS — Action Plan

Updated: 2026-11-19. Baseline: main92ed0ab after PR #2.

## Current
Foundation PR #1 merged9012dd1; instructor UI/BUG-006 PR #2 merged92ed0ab. ASSIGN-01 IN_PROGRESS: model/services/snapshots and instructor selection/review/confirmation/history/detail/cancellation delivered to source main; student assignment pages/progress/feedback/reporting not built. No student submissions/completion controls.

BUG-006 FIXED_VERIFIED for UUID JSON defect on successful independently retrieved pre-merge checks44668593439 and44668981076 for ddc000b. Earlier f52a592 failed run44667767312 retained: owner-supplied log296tests/9errors; no passing count inferred. BUG-005 remains verified on owner-reported CI after8e80939. Foundation pre-merge checks independently retrieved; post-PR1 run44665898145 owner-reported. Post-PR2 main CI NOT VERIFIED.

## Documentation refresh
README corrected; LOCAL_TESTING.md adds safe local setup, automated checks, synthetic account/MFA/class/lesson/assignment/student/PDF walkthroughs and evidence recording. docs/README.md indexes every feature guide and reconciles historical increment wording. ASSIGNMENTS.md captures merged workflow/limitations. DECISIONS.md distinguishes proposals from actual DB PDF storage/session choices; VALIDATION.json replaces initial-only current-status claims with attributed evidence and a retained historical source. Guide commands/browser steps were NOT executed while preparing docs. No application/settings/flags/credentials/schema changed.

## Next
1. Verify post-PR2 main CI and record actual source/jobs/counts only if retrieved.
2. Execute LOCAL_TESTING.md against isolated local PostgreSQL with synthetic data; record browser results, not just CI.
3. Review assignment review/confirm/cancel/session concurrent interleavings and durable nonce/idempotency design; no exactly-once guarantee today.
4. Build student read-only assigned lesson list/detail with existing student-session isolation.
5. Add instructor-controlled progress/status/feedback, then reporting; assignment-aware document delivery needs separate authorization/safety.

## Release gates retained
BRAND-01/DOC-01/LESSON-01 browser/security/operations acceptance, E08-05 concurrency/browser extensions, BUG-003 remaining acceptance; shared-device/back/reset/sign-in races, audit/throttling/recovery/approved session policy/TLS/log-redaction/privacy/retention/email/deployment/backup-restore/training remain open. PDFs default off, controlled synthetic trial only; no malware scanning/full parser. Python3.14 unverified. No production authorization or runtime deployment/migration performed.

Every implementation/fix commit updates this plan,TICKETS.md,IMPLEMENTATION_STATUS.md and affected current guides/decisions/validation/index. Preserve earlier failures and distinguish authoring checks, supplied logs, owner reports and independent evidence. No unattended documentation synchronization is claimed.

[Pre-refresh plan/history](https://github.com/pavanjains/lms/blob/92ed0ab127149081483c8044ab41cf4e4ee9f82e/ACTION_PLAN.md).
