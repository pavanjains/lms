# Robotics LMS — Action Plan

Updated 2026-11-22 for fix/skip-to-content. Source baseline main 6e3dd234417f831acd3a5362cad3adb0e4fb6d84. Skip-link fix is authored in the feature branch, not verified or merged. No production authorization.

## Current increment
Owner reported Skip to content did nothing on all pages. Shared base already had href=#main and matching main ID, but no tabindex/focus indicator. Add tabindex=-1 to main and explicit link/target focus outlines, preserving visible native fragment navigation without JavaScript, autofocus or positive tabindex. This addresses a source focusability gap; browser root cause/acceptance not independently reproduced. Six rendered-structure regression methods and browser guide docs/SKIP_LINK.md are authored. Python syntax/compile and authored HTML structure checked only; Django/Ruff/rendering/browser/CI pending.

Owner reported CI passed after docs commit 6e3dd23 at 18:38 EST; associated by context, exact run/tested SHA/runtime/count not supplied or independently retrieved. Not verification of this later feature commit.

## Merged source and retained evidence
PR #5 roster assignments merged at a0cd91b78f7d38c885e64f526ade8285b2b82e53, guarded head 83c86a3; 15 new regression methods including the authentication-order correction. PR #6 BUG-003 HTTPS/CSRF verification merged at 7a82d695528d1b0db4ea20dda2ca04b82173464d, guarded head d2784b9; 10 new methods, tests/docs only. Independently retrieved successful pre-merge runs: #5 45081121549/45081792433; #6 45082944989/45083255954. No passing count exposed. Earlier post-PR6 main pass at 18:30 EST was owner-reported only; PR #5 merge-specific run remains unverified. Earlier UUID, feedback-length and roster-test failures remain in TICKETS.md/VALIDATION.json.

## Next gates
1. Review/commit skip-link branch, verify exact-head CI and execute keyboard/Enter/focus/next-Tab/outline/no-JavaScript checks on public, staff, student, MFA and error pages. Test short/long pages and relevant browsers. Structural tests are not browser execution; do not mark fixed from CI alone.
2. BUG-003 remains REVIEW: execute synthetic onboarding browser checklist and verify token-path logging redaction in actual application/server/proxy/APM/mail/retained sinks. No production redaction implemented/verified.
3. ASSIGN-01/02 and ROSTER-ASSIGN-01 remain IN_PROGRESS: roster keyboard/count/select-page/no-JavaScript, previews/errors/final Confirm/cancel/back/reload/history; student A/B/stale-update/identity-switch/reset/expiry/revocation acceptance. Prior assignment/Confirm, progress/reload and status-only privacy are owner-reported, not full acceptance.
4. Verify migration 0003_assignment_progress application on the intended database; already on main, deployment unverified. Inspect status/plan and back up before deliberate database writes. Do not infer application from code/CI/browser reports or rerun bootstrap.
5. Progress history/reporting, durable review-token concurrency and possible summary/instructions TextField service length enforcement remain separate. Preserve E08-05, branding/library/document, audit/throttling/recovery/session/TLS/logging/privacy/retention/mail/file safety/deployment/backup/restore/training gates. Python 3.14 unverified; PDFs restricted, student document delivery unapproved.

## Workflow
Implementation uses feature branches/PRs, final-head checks/review and expectedHeadSha merges. Confirm every write with exact payload. Update action/tickets/status/affected guides/validation; preserve local data/changes/credentials and all earlier failure attribution. No deployment/migration/flag/account/security-guard change or production approval in this skip-link increment. Earlier detailed snapshot: https://github.com/pavanjains/lms/blob/6e3dd234417f831acd3a5362cad3adb0e4fb6d84/ACTION_PLAN.md
