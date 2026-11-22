# Development Tickets and Fix Ledger

## BUG-003 — REVIEW; HTTPS regression coverage authored 2026-11-22
Branch fix/bug-003-onboarding-verification, baseline a0cd91b. Historical scope is instructor-onboarding null-origin/CSRF failure, not migration 0003 or the skip-link defect. Historical ledger records 24453d6 no-referrer to same-origin correction and local confirmation; full browser acceptance and token-path logging remained open. Current implementation retains same-origin and normal CSRF enforcement.

Add 10 HTTPS/CSRF methods for Origin/Referer success and rejection across invite/resend/activate, missing CSRF and privacy/one-time behavior. Existing tests unchanged. Correct E05_ONBOARDING.md's stale no-referrer text and add browser/logging gates. No runtime/settings/migration/credential changes. Python syntax/compile checked only; new CI/browser/PostgreSQL verification pending. No FIXED_VERIFIED or production claim. Historical scope source: https://github.com/pavanjains/lms/blob/ded6acb393cb80f20bd3394e6f7c3724ccb40ec7/docs/TICKETS.md

## Roster evidence update
PR #5 merged at a0cd91b78f7d38c885e64f526ade8285b2b82e53 with expected head 83c86a3. Checks 45081121549 and 45081792433 independently retrieved successful before merge; no passing count. Supersedes pending-retest status below, preserves the earlier failure; browser acceptance remains pending. Post-merge CI unverified.

## Historical roster ledger retained
Updated 2026-11-22; source baseline 88524ab.

## ROSTER-ASSIGN-01 — IN_PROGRESS
Branch feature/class-roster-assignments: per-page roster selection, preselected recipients, active lesson previews, signed review and explicit confirmation, POST cancellation, return to class and scoped history. Existing service/authorization and central history retained; no migration or exactly-once guarantee. 15 new regression methods authored; only Python syntax/compile checked. Django, Ruff, rendering, browser and PostgreSQL NOT RUN by the author. CI/acceptance pending; procedures in ASSIGNMENTS.md.

## Retained status and evidence
ASSIGN-01/02 remain IN_PROGRESS. PR #4 merged at f3cc9e2 per HANDOFF.md. Owner-reported only: CI for 88524ab (runtime/count unknown), assignment after Confirm, progress/reload and status-only privacy. Migration 0003 deployment unverified.

Retain BUG-006 UUID failure: f52a592 run 44667767312, owner-supplied log, 296 tests/9 errors; fixed ddc000b. Retain feedback-length failure: c9b76e2, owner-supplied log without run ID, 338 tests/2 failures from one test; fixed 23a9d2d. Retrieved successful check IDs/attribution remain in VALIDATION.json, with no derived passing count.

Skip-link defect is reported, undiagnosed and not fixed here. Stale/A-B/identity-switch/back/reset/expiry/revocation, concurrency, history/reporting, file safety, Python 3.14 and production gates remain open. E08-05 IN_PROGRESS, BUG-003 REVIEW; BUG-005/E08-08/BUG-004 retain earlier owner-report attribution. No production approval.

Historical ledger, including prior statuses and CI attribution:
https://github.com/pavanjains/lms/blob/88524ab8788fc61b72c2a4d8ff19ccbdee38d159/docs/TICKETS.md

## Roster authentication-order test defect — FIX_AUTHORED_PENDING_RETEST
Owner-supplied log: 353 tests in 13.113s, one failure at test_roster_assignments.py:196 (302 != 405), clean system check, exit 1; run ID/revision/runtime unknown. The CSRF client was authenticated but self.client was anonymous. Retrieved StaffAuthMiddleware redirects before view dispatch. Correct only the test: anonymous/password-only PUT redirects to login; MFA-verified PUT returns 405; CSRF checks remain. Replacement-method syntax checked, Django retest not run by author. No passing count claimed.
