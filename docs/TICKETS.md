# Development Tickets and Fix Ledger

Updated: 2026-11-18, 20:23 EST.

## Rules / history
REVIEW = authored awaiting verification; IN_PROGRESS = partial acceptance; CI_PASSED is evidence-specific. [Previous full ledger](https://github.com/pavanjains/lms/blob/873cbb4ebb9c028c0985c6d2135c46572c2241e7/docs/TICKETS.md) preserves E01–E22, BUG and commit evidence. Unaffected statuses unchanged; Markdown IDs are not GitHub Issues.

## E08
| Ticket | State | Evidence / remaining work |
|---|---|---|
| E08-01 | CI_PASSED | 6929d69 owner November 15 15:50 report; run 43758274124, fetch failed/count unknown. |
| E08-02 | REVIEW | 7e3792c services; no supplied CI result. |
| E08-03 | REVIEW | 7e3792c policies; no supplied CI result. |
| E08-04 | REVIEW | d437edf browser UI; CI/browser pending. |
| E08-05 | IN_PROGRESS | 7f97933 eleven concurrency methods; execution/browser pending, not coverage for newer creation/reset services. |
| E08-06 | REVIEW | 873cbb4 class-scoped student creation; CI/browser/race extension pending. |
| E08-07 | REVIEW | Student password reset/credential receipt/session revocation and tests authored; CI/browser/races pending. |

E08-07 scope: MFA/current active staff, active same-organization class, active instructor membership unless owner, active STUDENT with profile and active enrollment. GET shows identity/confirmation only; POST generates cryptographic random password, validates/hashes, removes target's unexpired database sessions transactionally, returns credential receipt without redirect. No staff reset, old-password retrieval, automatic expiry/forced change, plaintext persistence/email/session/message/URL or auto-login. No new migration/flag activation/runtime data action by source commit. Unsupported session engines rejected before password change.

Tests authored, NOT RUN here: hash replacement/reissue, role/org/class/enrollment/MFA/gate boundaries, targeted session cleanup/rollback, backend rejection, validator failure, GET/confirmation, receipt non-retrieval, CSRF/origin and staff-session preservation. No passing count inferred; new SHA assigned at commit, CI PENDING. Browser copies/history/screenshots not erasable; response-only display is not single-use authentication. Audit/throttling and credential delivery approval remain blockers.

Only supplied recent passing run https://github.com/pavanjains/lms/actions/runs/43758274124 is owner-reported E08-01, not independently retrieved. No local migration/manual/updated passing counts inferred.

## Carry-forward
E05-01 CI_PASSED; E05-02/03/04/05 IN_PROGRESS; E05-06 CI_PASSED with manual/new control checks open; E05-07 REVIEW 666eee6; E05-08 TODO; E05-09 IN_PROGRESS; E05-10 TODO. E01–E03 partial/lockfile open. E04-02 DONE; E04-01/03/04 CI_PASSED with gaps; E04-06 IN_PROGRESS; E04-05/07/08/09/10 staff recovery/last-owner/throttling/session open. Student reset does not complete staff password recovery. E06–E22 otherwise preserved baseline. Python 3.14 support unverified.

## BUG history
BUG-001 FIXED_VERIFIED: ef6b96c bootstrap ordering; owner November 15 08:11 log 50 tests/four errors/46 passed; pass reported 08:24.

BUG-002 FIXED_VERIFIED: 1b4a5dd django.contrib mail import fixed to django.core in e3bcfcb. Owner 13:21 log 83 entries in 0.897s/one import error/82 passed; no onboarding methods executed, fourteen retained. Owner pass 13:28 without URL/count; cd1f580 recorded report.

BUG-003 REVIEW: 24453d6 same-origin header/five added CSRF methods/fourteen originals retained. Owner null-origin POST 403 November 15 14:39:31; local fix confirmed 15:07. Full browser/activation/deactivation and separate fix CI unavailable; no CSRF bypass/log redaction still open. Older ef6b96c/d60ab7d/0ce5595 owner-pass reports and inferred 031b843 failure association remain in linked ledger. No independent Actions claims.
