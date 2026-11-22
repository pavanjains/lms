# Implementation Status

## Current verification increment, 2026-11-22
BUG-003 remains REVIEW. On fix/bug-003-onboarding-verification, baseline a0cd91b, 10 new HTTPS/CSRF methods and updated onboarding/browser/logging guidance are authored. Existing same-origin fix and CSRF/security/runtime behavior unchanged. Syntax/compile checked; new Django/Ruff/rendering/browser/PostgreSQL verification NOT RUN. Token-path redaction needs actual hosting/sink verification; no production redaction or browser acceptance claimed.

PR #5 merged at a0cd91b78f7d38c885e64f526ade8285b2b82e53 after successful independently retrieved pre-merge checks 45081121549 and 45081792433, guarded at 83c86a3. No passing test count; post-merge CI unverified. Supersedes historical roster pending-retest notes below, not remaining browser/security/deployment gates.

## Historical implementation notes retained
Updated 2026-11-22; feature baseline main 88524ab. No production authorization.

Existing staff/MFA, classroom, student/session, lesson/PDF and assignment snapshot/read-only student features remain in source. PR #4 progress/feedback merged at f3cc9e2 per HANDOFF.md; students see status only. Migration 0003 deployment remains unverified.

ROSTER-ASSIGN-01, branch feature/class-roster-assignments, adds per-page roster selection, preselection, lesson previews, explicit signed confirmation, POST review cancellation, class return and independently paginated class history. Existing services, central history, progress controls and student queries remain in use. No migration, automatic enrollment assignments, student write controls, feedback exposure or durable exactly-once guarantee.

15 new regression methods are authored. Python syntax/compile checks executed; Django, Ruff, template rendering, browser and PostgreSQL NOT RUN by the author. New-flow CI/acceptance pending; no runtime passing count claimed. ASSIGN-01/02 remain IN_PROGRESS. Owner-reported only: CI for 88524ab and prior assignment/progress/reload/privacy browser checks. Remaining gates include skip-link defect, stale/A-B/identity-switch/back/reset/expiry/revocation, token concurrency, history/reporting, TextField validation, file safety, Python 3.14, security/operations/deployment and production acceptance.

Earlier UUID and feedback-length failures remain in TICKETS.md/VALIDATION.json. Prior detailed implementation/evidence/release gates:
https://github.com/pavanjains/lms/blob/88524ab8788fc61b72c2a4d8ff19ccbdee38d159/docs/IMPLEMENTATION_STATUS.md

## Roster CI failure and test-only correction
Owner-supplied log reports 353 tests, one failure, 13.113s, clean system check and exit 1; exact run/revision/runtime unverified. Test expected 405 from an anonymous PUT, but staff middleware returned the correct login redirect. Test now separates anonymous/password-only redirects from MFA-verified 405. Application code unchanged. Replacement-method syntax checked; corrected-suite CI and browser acceptance pending.
