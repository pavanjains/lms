# Robotics LMS — Action Plan

Updated 2026-11-22 after PR #6 merge and the owner's 18:30 EST CI report. Audited source baseline: main 7a82d695528d1b0db4ea20dda2ca04b82173464d, before this documentation-only commit. No production authorization.

## Current source and evidence
- PR #5 merged class-roster assignments at a0cd91b78f7d38c885e64f526ade8285b2b82e53, guarded at head 83c86a3776a509350c02df74b4b3dbbb7d026e35. Includes roster selection, lesson previews, explicit signed review/confirmation, return to class, scoped history and 15 regression test methods including the authentication-order correction.
- PR #6 merged BUG-003 verification at 7a82d695528d1b0db4ea20dda2ca04b82173464d, guarded at head d2784b90c3826c9a8502aa6ea432167b017768c1. Adds 10 HTTPS/CSRF regression methods and onboarding/browser/logging guidance; no runtime security change.
- Independently retrieved successful pre-merge checks: PR #5 runs 45081121549 and 45081792433; PR #6 runs 45082944989 and 45083255954. No passing counts exposed.
- Latest post-merge CI success is owner-reported after PR #6; run ID, exact tested SHA, runtime and test count were not supplied or independently retrieved. This does not verify a later documentation commit or retroactively establish a PR #5 merge-specific run.
- Earlier failures are retained in TICKETS.md and VALIDATION.json, including the owner-supplied 353-test/one-failure roster run. No total is inferred for successful runs.

## Status and next actions
1. BUG-003 remains REVIEW. Execute the synthetic onboarding browser checklist in docs/E05_ONBOARDING.md: invite/resend/activation, invalid/used/expired/revoked links, same-origin and approved HTTPS behavior, sign-out/MFA, privacy and back/reload. Verify token-path redaction in actual application/server/proxy/APM/mail/retained sinks before operational enablement. No hosting-specific redaction has been implemented or verified.
2. ASSIGN-01, ASSIGN-02 and ROSTER-ASSIGN-01 remain IN_PROGRESS. Verify the roster keyboard/count/select-page/no-JavaScript flow, errors, final Confirm, cancel/back/reload, scoped history and student A/B isolation. Prior assignment after Confirm, progress persistence after reload and status-only privacy were owner-reported only, not full acceptance. Procedures: docs/ASSIGNMENTS.md and docs/LOCAL_TESTING.md.
3. Diagnose the separate skip-to-content defect reported on all pages. It is not BUG-003 and is not fixed by either merge.
4. Verify existing migration 0003_assignment_progress application on the intended database. It is already on main; deployment/application remains unverified. Inspect status/plan and back up the intended database before any deliberate migration. Do not infer application from source, CI or browser reports.
5. Keep progress history/reporting, durable review-token concurrency and possible service enforcement of Lesson/LessonAssignment summary/instructions TextField length limits as separate work. No exactly-once review-token guarantee.
6. Preserve remaining E08-05, BUG-003, branding/library/document browser/security/operations, audit, throttling, recovery, session policy, TLS, log redaction, privacy/retention, mail, file safety, deployment, backup/restore and training gates. Python 3.14 remains unverified; PDFs remain restricted and student document delivery is not approved.

## Working rules
Implementation uses feature branches/PRs; merges require final-head checks and expectedHeadSha. Every external write requires exact-payload approval. Direct main writes are documentation-only when explicitly requested. Update action plan, tickets, implementation status, affected guides and attributed validation with implementation/fix commits. Preserve local changes, credentials and database data; do not rerun bootstrap on the existing installation. Record only observed/retrieved/reported evidence and never replace earlier failures with a generic pass.

This documentation update does not run tests, deploy, migrate, change flags/accounts/credentials, close acceptance tickets or approve production. Current evidence here and in VALIDATION.json supersedes dated authoring-time CI-pending notes in feature guides; those guides remain procedures, not execution reports.

Previous snapshot and historical links: https://github.com/pavanjains/lms/blob/7a82d695528d1b0db4ea20dda2ca04b82173464d/ACTION_PLAN.md
