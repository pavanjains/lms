# Development Tickets and Fix Ledger

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
