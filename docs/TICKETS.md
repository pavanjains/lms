# Development Tickets and Fix Ledger

Updated: 2026-11-18, 19:58 EST.

## Rules/history
REVIEW means authored awaiting verification; CI_PASSED is evidence-specific, not manual/production acceptance. [Complete preceding ledger](https://github.com/pavanjains/lms/blob/7e3792c115769739fc1a200db1bc366123a700b2/docs/TICKETS.md) preserves E01–E22, BUG histories and commit evidence; unaffected statuses unchanged. Markdown IDs are not GitHub Issues. No inferred counts or independent Actions claims.

## E08
| Ticket | State | Evidence / remaining work |
|---|---|---|
| E08-01 | CI_PASSED | 6929d69, owner November 15 15:50 EST report; run 43758274124. Fetch failed, count unknown; local migration/manual checks not implied. |
| E08-02 | REVIEW | 7e3792c services; no CI result supplied. |
| E08-03 | REVIEW | 7e3792c scoped policies; no CI result supplied. |
| E08-04 | REVIEW | Browser UI/forms/routes/navigation and UI tests authored; CI/manual browser acceptance pending. |
| E08-05 | TODO | PostgreSQL races/shared-instructor end-to-end acceptance. |

E08-04: /staff/classes/ list/detail; owner create/archive/instructor changes; assigned-instructor enrollment constrained by existing student visibility. Every write uses existing transactional services. Confirmation and CSRF required, GET read-only, same-origin response policy, private/no-store staff responses. Active rosters use safe field projections, selectors limited to authorized same-organization IDs. Archived class details omit roster/management controls. No reactivation or student creation. No migration/flag activation/runtime writes by source commit.

Tests authored, NOT RUN here. UI tests cover scopes, permissions, forged selectors, confirmation, archive, membership loss, CSRF valid-token origin rejection/success, MFA/gate/method checks. Existing service tests unchanged: suspected method-level override_settings fixture issue was rejected on review, not a confirmed bug.

E08-01 run: https://github.com/pavanjains/lms/actions/runs/43758274124 . E08-02/03 commit 7e3792c has no supplied CI result. New E08-04 SHA assigned on commit; CI pending.

## E05 and foundation carry-forward
E05-01 CI_PASSED; E05-02/03/04/05 IN_PROGRESS; E05-06 CI_PASSED with new control/manual checks open; E05-07 REVIEW 666eee6; E05-08 TODO; E05-09 IN_PROGRESS; E05-10 TODO. E01–E03 partial/lockfile open. E04-02 DONE; E04-01/03/04 CI_PASSED with gaps; E04-06 IN_PROGRESS; E04-05/07/08/09/10 recovery/last-owner/throttling/session tasks open. E06–E22 otherwise preserved baseline. Python 3.14 support unverified.

## BUG history
BUG-001 FIXED_VERIFIED: bootstrap full_clean ordering, ef6b96c. Owner November 15 08:11 log: 50 tests/four errors/46 passed; owner pass 08:24 after fix.

BUG-002 FIXED_VERIFIED: 1b4a5dd mail import corrected e3bcfcb, django.contrib to django.core. Owner 13:21 log: 83 entries in 0.897s, one module-import error/82 passed; no onboarding methods executed. Fourteen retained. Owner pass 13:28, URL/count unknown; cd1f580 records report.

BUG-003 REVIEW: 24453d6 no-referrer to same-origin, five added CSRF methods/fourteen originals retained. Owner null-origin invitation POST 403 November 15 14:39:31; local fix confirmed 15:07. Browser/version/full activation/deactivation checks unavailable. New separate fix CI not supplied; browser header generation not simulated by test client. No CSRF bypass; token-path log redaction remains open.

Historical evidence in linked ledger remains authoritative: ef6b96c/d60ab7d/0ce5595 owner-reported passes 08:24/08:30/08:51; earlier 031b843 failure association inferred; no separately supplied documentation CI or independently retrieved Actions result. E08-01 pass is not retrospective manual acceptance of E05. All release gates remain.
