# Development Tickets and Fix Ledger

Updated: 2026-11-18, 20:17 EST.

## Rules and preserved history
REVIEW = authored awaiting verification; IN_PROGRESS = partial acceptance; CI_PASSED does not imply browser/production approval. [Complete previous ledger](https://github.com/pavanjains/lms/blob/7f97933d1666b443f5d12aba01f98ac9427939c4/docs/TICKETS.md) preserves E01–E22, E05, BUG histories and all commit evidence. Unaffected statuses unchanged; Markdown IDs are not GitHub Issues.

## E08
| Ticket | State | Evidence / remaining work |
|---|---|---|
| E08-01 | CI_PASSED | 6929d69 owner November 15 15:50 report; run 43758274124, fetch failed/count unknown. |
| E08-02 | REVIEW | 7e3792c services; no supplied CI result. |
| E08-03 | REVIEW | 7e3792c policies; no supplied CI result. |
| E08-04 | REVIEW | d437edf browser UI; CI/browser pending. |
| E08-05 | IN_PROGRESS | 7f97933 eleven concurrency methods authored; no CI execution evidence, browser acceptance open. New student-creation service not covered by those races. |
| E08-06 | REVIEW | New authorized-class student creation service/form/UI/tests authored; CI/browser/race-extension pending. |

E08-06 acceptance scope: owner or active assigned instructor with current MFA creates fixed STUDENT account, grade profile and initial enrollment in one transaction. Initial shared access follows authorized class enrollment, not permanent creator access. Password validated/hashed, blank email, staff/superuser false; no arbitrary role/organization fields, username availability endpoint, plaintext credential echo, auto-login, email, reset or student-sign-in route. Global username uniqueness follows existing User schema; conflicts return generic errors and roll back.

Tests authored, NOT RUN here: account/profile/enrollment consistency; password hashing/no staff login; shared/revoked access; owner/unassigned/cross-org/archive/MFA/gate boundaries; validation/duplicate/rollback; UI confirmation/injection/CSRF/origin checks. No migration or runtime data/flag changes by source commit. New SHA assigned at commit; CI PENDING.

Only supplied recent passing run: https://github.com/pavanjains/lms/actions/runs/43758274124 , owner-reported for E08-01, not independently retrieved; no test count or local migration/browser success inferred. New methods are not covered by prior reports.

## Carry-forward
E05-01 CI_PASSED; E05-02/03/04/05 IN_PROGRESS; E05-06 CI_PASSED with manual/new control checks open; E05-07 REVIEW 666eee6; E05-08 TODO; E05-09 IN_PROGRESS; E05-10 TODO. E01–E03 partial/lockfile open. E04-02 DONE; E04-01/03/04 CI_PASSED with gaps; E04-06 IN_PROGRESS; E04-05/07/08/09/10 recovery/last-owner/throttling/session open. E06–E22 otherwise preserved baseline; E08-06 is a new classroom-scoped creation slice, not completion of broader student-access epics. Python 3.14 support unverified.

## BUG history
BUG-001 FIXED_VERIFIED: ef6b96c bootstrap full_clean ordering; owner November 15 08:11 log 50 tests/four errors/46 passed; pass reported 08:24.

BUG-002 FIXED_VERIFIED: 1b4a5dd django.contrib mail import fixed to django.core in e3bcfcb. Owner 13:21 log 83 entries in 0.897s/one import error/82 passed; no onboarding methods executed, fourteen retained. Owner pass 13:28 without URL/count; cd1f580 records report.

BUG-003 REVIEW: 24453d6 same-origin header/five added CSRF methods/fourteen originals retained. Owner null-origin POST 403 November 15 14:39:31; local fix confirmed 15:07. Full browser/activation/deactivation verification and separate fix CI unavailable. No CSRF bypass; token-path log redaction open. Older ef6b96c/d60ab7d/0ce5595 owner-pass reports and inferred 031b843 failure association remain in linked ledger. No new passing counts or independent Actions claims.
