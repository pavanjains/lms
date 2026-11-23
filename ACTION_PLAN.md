# Robotics LMS — Action Plan

Updated 2026-11-22. Current branch fix/lesson-text-validation, baseline main ff2f68c1e67b6a24d3d8a6854f6187b3f89e49b6. No production authorization.

## Current code task
Explicit summary/instructions length checks after normal full_clean in lesson create/edit and assignment source/snapshot creation. Shared helper reads existing model limits2000/20000, rejects with field errors, never truncates; preserves normalization and transactional writes. No model/schema/migration/authorization/feedback/cancel/progress/archive changes. Twelve regression methods authored. New helper/test modules syntax/compile checked only; Django/Ruff/drift/PostgreSQL/CI pending. Guide/commands: docs/LESSON_LIBRARY.md. Review exact payload, verify final-head CI, then PR/expectedHeadSha merge; do not infer a passing count.

## Carry-forward
Skip-link PR7 merged at ff2f68c, guarded319b980; pre-merge checks45085015833/45085254574 independently successful. Owner reported merge CI passed at19:24 EST (run/testedSHA/runtime/count unknown). Actual focus/next-Tab/outline/no-JavaScript/cross-browser acceptance remains open. BUG003 REVIEW for onboarding browser and token-path logging. ASSIGN01/02/ROSTER-ASSIGN01 IN_PROGRESS for browser A/B/stale/identity-switch/back/reset/expiry/revocation/roster acceptance. Prior assignment/progress/privacy browser results remain owner-reported.

Verify migration0003 application on intended DB after status/plan and backup; already in source, no bootstrap rerun or inferred deployment. Progress history/reporting and durable review-token concurrency remain separate; no exactly-once guarantee. Preserve E08-05, branding/library/document/file safety/student delivery, audit/throttling/recovery/session/TLS/logging/privacy/retention/mail/deployment/backup/training gates. Python3.14 unverified; PDFs restricted.

All implementation/fix commits update action/tickets/status/affected guides/validation. Confirm each external write; feature branch/PR, guarded merges, preserve local changes/data/credentials and earlier failures. Prior detailed plan/evidence: https://github.com/pavanjains/lms/blob/ff2f68c1e67b6a24d3d8a6854f6187b3f89e49b6/ACTION_PLAN.md
