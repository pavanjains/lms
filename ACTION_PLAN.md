# Robotics LMS — Action Plan

Updated 2026-11-25. Current branch docs/local-mode-mfa-lan, baseline main 70ce95d9c981eeeb2303a76003683677569f95da (PR #9 merge). No production authorization.

## Current task
Documentation only: local-mode and LAN setup in docs/LOCAL_TESTING.md section 3a, with matching TICKETS.md and IMPLEMENTATION_STATUS.md entries and this plan. No code, settings or database change. Review the exact payload, verify the PR head check independently, then merge with expectedHeadSha; do not infer a passing count.

## Recently merged
PR #8 merged at 03f332f: lesson and snapshot summary/instructions length checks (2000/20000, no truncation, no existing-data repair). Head runs 45091368598 and 45092648047 independently successful; post-merge CI not independently verified.

PR #9 merged at 70ce95d: local-only installation-wide MFA policy (MFA-POLICY01) with owner-page checkbox, audit records, migration accounts/0003_installation_mfa_policy and staff login/middleware enforcement. Head 83f2715 check run 139469414958 independently successful, no passing count; an earlier owner-supplied log with one failing test (a test-helper defect) is preserved in TICKETS.md. Owner reports migrate applied locally and the checkbox visible. Merge-commit CI not independently verified.

## Open acceptance
MFA-POLICY01: browser check that password-only sign-in works with the policy off for owners and instructors in every organization, that turning MFA back on forces verification again, that existing authenticators still work, that students never reach staff pages, and that the audit record appears. Defaults keep MFA required; production settings refuse to start when the local variables are set; never enable local mode with real data.

LAN-01: owner reports staff sign-in, student sign-in and lesson creation working from a second computer using DJANGO_ALLOWED_HOSTS and runserver 0.0.0.0:8000; the earlier failure was not diagnosed. Not implemented: a local-only trusted-origin or public-origin setting (invitation links keep a localhost address), HTTPS, hardened serving or a separate network zone for student routes. Plain HTTP on a development server is acceptable only on a trusted network.

## Carry-forward
Skip-link PR7 merged at ff2f68c, guarded319b980; pre-merge checks45085015833/45085254574 independently successful. Owner reported merge CI passed at19:24 EST (run/testedSHA/runtime/count unknown). Actual focus/next-Tab/outline/no-JavaScript/cross-browser acceptance remains open. BUG003 REVIEW for onboarding browser and token-path logging. ASSIGN01/02/ROSTER-ASSIGN01 IN_PROGRESS for browser A/B/stale/identity-switch/back/reset/expiry/revocation/roster acceptance. Prior assignment/progress/privacy browser results remain owner-reported.

Migrations: accounts 0003_installation_mfa_policy was applied locally per the owner's report. Lessons migration0003 assignment-progress application on the intended DB is still unverified; check status/plan and back up first, with no bootstrap rerun or inferred deployment. Progress history/reporting and durable review-token concurrency remain separate; no exactly-once guarantee. Preserve E08-05, branding/library/document/file safety/student delivery, audit/throttling/recovery/session/TLS/logging/privacy/retention/mail/deployment/backup/training gates. Python3.14 unverified; PDFs restricted.

All implementation/fix commits update action/tickets/status/affected guides/validation. Confirm each external write; feature branch/PR, guarded merges, preserve local changes/data/credentials and earlier failures. Prior detailed plan/evidence: https://github.com/pavanjains/lms/blob/ff2f68c1e67b6a24d3d8a6854f6187b3f89e49b6/ACTION_PLAN.md
