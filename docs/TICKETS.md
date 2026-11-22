# Development Tickets and Fix Ledger

Updated 2026-11-22 after the owner's 18:30 EST CI report. Audited main baseline 7a82d695528d1b0db4ea20dda2ca04b82173464d, before this documentation-only update. Markdown ticket IDs are not GitHub issue numbers; this is the existing ticket ledger, not a new Ticket.md.

## BUG-003 — REVIEW; verification increment MERGED, browser/logging acceptance open
Historical defect: instructor-onboarding null-origin/CSRF failure, not migration 0003 or the skip-link issue. Earlier correction 24453d6 changed no-referrer to same-origin; historical local confirmation and included CI pass were owner-reported. Existing implementation retains same-origin and normal CSRF enforcement.

PR #6 merged at 7a82d695528d1b0db4ea20dda2ca04b82173464d with expected head d2784b90c3826c9a8502aa6ea432167b017768c1. Ten new HTTPS/CSRF methods cover invite/resend/activation, Origin/Referer success, null/foreign/scheme/port rejection, missing/unsafe Referer, missing CSRF and privacy/one-time/no-auto-login behavior. Existing onboarding tests retained. Updated E05_ONBOARDING.md corrects stale no-referrer wording and adds browser/logging gates. This increment changed tests/documentation only, not runtime settings, security guards, migrations, flags or credentials.

Independently retrieved successful checks on the PR head: run 45082944989/check 137394965797 and run 45083255954/check 137395959713. No passing count exposed. Latest post-merge pass is owner-reported after PR #6, not independently retrieved; run ID, tested SHA, runtime and count unspecified. No FIXED_VERIFIED or production claim. Execute the synthetic browser checklist and verify real token-path logging sinks before closing the remaining acceptance scope.

Historical scope: https://github.com/pavanjains/lms/blob/ded6acb393cb80f20bd3394e6f7c3724ccb40ec7/docs/TICKETS.md

## ROSTER-ASSIGN-01 — IN_PROGRESS; source MERGED, browser acceptance pending
PR #5 merged at a0cd91b78f7d38c885e64f526ade8285b2b82e53 with expected head 83c86a3776a509350c02df74b4b3dbbb7d026e35. Roster per-page selection/count/select-page, preselected students, lesson previews, existing signed review/explicit confirmation, POST review cancellation, signed class return and independently paginated scoped history are in main. Central history and transactional assignment services retained; no feedback in roster, automatic enrollment assignment, new migration or durable exactly-once guarantee. Fifteen regression methods are authored.

Independently retrieved successful head checks: run 45081121549/check 137389292906 and run 45081792433/check 137391367330. No passing count exposed. A PR #5 merge-specific CI run remains unverified. Browser keyboard/no-JavaScript/selection/pagination/error/Confirm/cancel/back/reload/history and A/B acceptance remain pending.

### Authentication-order test defect — corrected; pre-merge CI verified
Retain owner-supplied log: 353 tests in 13.113s, one failure at test_roster_assignments.py:196 (302 != 405), system check clean, exit 1; exact run/revision/runtime not supplied. The CSRF client was authenticated but self.client was anonymous, so StaffAuthMiddleware correctly redirected before view dispatch. Fix 83c86a3 checks anonymous/password-only redirects, then MFA-verified 405, retaining CSRF assertions. Application guards unchanged. Later successful checks above supersede pending-retest status, not the failure record; do not reuse 353 as a passing total.

## ASSIGN-01 and ASSIGN-02 — IN_PROGRESS
Assignment snapshot/student UI and instructor status/feedback are in source. PR #4 merged at f3cc9e2 per the earlier handoff. Students see status only, not feedback or progress controls. Prior assignment after final Confirm, progress persistence after reload and status-only privacy checks are owner-reported, not independently observed/full browser acceptance. Migration 0003 application is unverified. History/reporting and durable review-token concurrency remain separate.

## Other open work and retained attribution
- Skip-to-content reported nonfunctional on all pages: undiagnosed, not fixed, separate from BUG-003.
- E08-05 remains IN_PROGRESS. E08-08/BUG-004 and BUG-005 retain earlier owner-report attribution. BUG-005 NumericPasswordValidator restoration after 8e80939 is not independently verified here.
- Branding/library/document acceptance, file safety/student document authorization, shared-device/identity-switch/back/reset/expiry/revocation/race acceptance and audit/throttling/recovery/approved sessions/TLS/privacy/retention/mail/deployment/backup/training remain open. Python 3.14 unverified; PDF/student file delivery not approved.

## Earlier failures and evidence retained
- BUG-006: f52a592 run 44667767312 failed; owner-supplied inspected log showed 296 tests, 9 errors, UUID JSON serialization. Fixed ddc000b. Pre-merge checks 44668593439 and 44668981076 independently retrieved successful; no passing total.
- Progress feedback length: c9b76e2 first CI failed; owner-supplied log, no run ID, 338 tests and 2 failures from one test. Fixed 23a9d2d. Checks 44846492681 and 44846822307 independently retrieved successful; no passing count.
- Student UI ebdb9ea checks 44834522871 and 44834596308 independently retrieved successful. Older PR #4 head f5ec991 checks 44847456934/44847462963 are retained as previously retrieved evidence from the earlier handoff, not re-retrieved in this update.
- Earlier owner reports for baseline/main CI, BUG-001/002 and other E05/E08 history remain in linked historical ledgers and VALIDATION.json. No old failure is erased or inferred passing count added.

The author has not executed Django, Ruff, template rendering, browser or PostgreSQL checks; Python syntax/compile checks and retrieved CI are distinct evidence. This documentation-only update performs no deployment, migration, credential/flag action or production approval. Its own future CI is not covered by an earlier pass report.

Prior full snapshot/history links: https://github.com/pavanjains/lms/blob/7a82d695528d1b0db4ea20dda2ca04b82173464d/docs/TICKETS.md
