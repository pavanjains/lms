# Development Tickets and Fix Ledger

Updated: 2026-11-18, 20:09 EST.

## Rules / preserved evidence
REVIEW = authored awaiting verification; IN_PROGRESS = partial acceptance; CI_PASSED is evidence-specific, not manual/production approval. [Previous complete ledger](https://github.com/pavanjains/lms/blob/d437edf410412d40e9fdb5d9b0d26b9f56d057ef/docs/TICKETS.md) preserves E01–E22, E05, BUG histories and commit evidence. Unaffected statuses unchanged. Markdown IDs are not GitHub Issues. No independently retrieved Actions results or inferred passing counts.

## E08
| Ticket | Status | Evidence / remaining work |
|---|---|---|
| E08-01 | CI_PASSED | 6929d69, owner November 15 15:50 report, run 43758274124. Fetch failed/count unknown. Local migration/manual acceptance not implied. |
| E08-02 | REVIEW | 7e3792c services; no CI result supplied. |
| E08-03 | REVIEW | 7e3792c policies; no CI result supplied. |
| E08-04 | REVIEW | d437edf UI/tests; CI and browser acceptance pending. |
| E08-05 | IN_PROGRESS | PostgreSQL concurrency test portion authored/REVIEW, NOT RUN here; new CI and shared-instructor browser acceptance pending. |

E08-01 run https://github.com/pavanjains/lms/actions/runs/43758274124 is owner-reported, not independent evidence. New E08-05 SHA assigned at commit.

## E08-05 scope
Eleven methods authored using TransactionTestCase, separate worker-local connections and real services. Leader holds an outer transaction after service write; main connection observes follower blocked by leader PID before releasing commit. Assertions cover normalized class-name conflict, duplicate assignment/enrollment row reuse, membership removal/archive/deactivation versus enrollment in both orders, and enrollment/end ordering preserving relationships. Only expected PermissionDenied/ValidationError become asserted outcomes; unexpected SQL/worker errors fail.

PostgreSQL only; SQLite explicitly skips, not a pass for locking semantics. CI adds PostgreSQL backend assertion and 15-minute job timeout; existing full test step discovers concurrency tests. Worker SQL/lock/event/future timeouts bound waits and thread connections close in finally. No service change, migration, runtime data, email or feature-flag activation.

Not covered: all schedules, arbitrary raw ORM writes, organization/role transfer races, password/session/browser behavior, E05 invitation races, sustained load or unrelated-organization throughput. MFA proof stubbed for service-level tests. Actual browser acceptance remains open; do not mark whole E08-05 DONE on CI alone.

## Carry-forward
E05-01 CI_PASSED; E05-02/03/04/05 IN_PROGRESS; E05-06 CI_PASSED with manual/new control checks open; E05-07 REVIEW 666eee6; E05-08 TODO; E05-09 IN_PROGRESS; E05-10 TODO. E01–E03 partial/lockfile open. E04-02 DONE; E04-01/03/04 CI_PASSED with gaps; E04-06 IN_PROGRESS; E04-05/07/08/09/10 recovery/last-owner/throttling/session open. E06–E22 otherwise preserved baseline. Python 3.14 support unverified.

## BUG history
BUG-001 FIXED_VERIFIED: bootstrap ordering ef6b96c; owner November 15 08:11 log 50 tests/four errors/46 passed; owner pass 08:24.

BUG-002 FIXED_VERIFIED: 1b4a5dd mail import corrected e3bcfcb django.contrib to django.core. Owner 13:21 log 83 entries in 0.897s, one module-import error/82 passed; no onboarding methods executed. Fourteen retained. Owner pass 13:28, URL/count unknown; cd1f580 recorded report.

BUG-003 REVIEW: 24453d6 same-origin header/five added CSRF methods/fourteen originals retained. Owner null-origin POST 403 November 15 14:39:31; local fix confirmed 15:07. Full activation/deactivation/browser checks and separately supplied fix CI remain open; no CSRF bypass and log redaction still open.

Older evidence retained in linked ledger: ef6b96c/d60ab7d/0ce5595 owner passes 08:24/08:30/08:51, earlier 031b843 failure association inferred; documentation commits have no separately supplied runs. No E08 CI report implies retrospective E05 manual acceptance. CI is not launch authorization.
