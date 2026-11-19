# Development Tickets and Fix Ledger

Updated: 2026-11-15, 15:50 EST. Parent: ../ACTION_PLAN.md.

## Evidence rules and preserved ledger
TODO = not implemented; IN_PROGRESS = partial; REVIEW = authored awaiting verification; CI_PASSED = passing evidence with manual gates possibly open; DONE = scoped acceptance met; FIXED_VERIFIED = corrected with evidence. User-reported and independent evidence remain distinct. Markdown tickets are not GitHub Issues.

[Preceding complete ledger](https://github.com/pavanjains/lms/blob/6929d69be5d009831588712694b43a3238006e32/docs/TICKETS.md) preserves E01–E22 ranges, E05 ticket statuses, commit evidence and BUG histories. Earlier baseline: https://github.com/pavanjains/lms/blob/24453d623785f1ff560c3444bcb5eedbb564a36c/docs/TICKETS.md . Unaffected statuses remain unchanged.

## E08
| Ticket | State | Evidence / scope |
|---|---|---|
| E08-01 | CI_PASSED | Owner reports 6929d69 workflow succeeded at 15:50 EST; run 43758274124 below. No count/logs supplied; local migration/manual checks not implied. |
| E08-02 | REVIEW | Transactional class/membership/enrollment services authored; fresh actor/MFA/flag checks and repeat-safe mutations. New CI pending. |
| E08-03 | REVIEW | Scoped class/student/roster policies authored; shared students do not grant other-class access. New CI pending. |
| E08-04 | TODO | Staff UI, CSRF, scoped selectors and browser acceptance. |
| E08-05 | TODO | PostgreSQL race and end-to-end shared-instructor acceptance. |

Run: https://github.com/pavanjains/lms/actions/runs/43758274124 . Fetch failed; Actions result not independently retrieved. No passing count inferred. Tests for the current increment authored, NOT RUN here. No migration, runtime data, email or feature-flag change.

## E08-02/03 boundary
Owner-only class creation/archive and instructor changes. Assigned instructors may end enrollment in active assigned classes; adding requires existing visibility through another/current active assigned class. Owners may enroll any eligible same-organization student. No student creator relation or student creation yet. Removed/inactive membership loses scope on a fresh policy call. Active student profiles only in directory; archived classes visible only to owners, no active roster access.

Current statuses are rechecked, not trusted from stale model instances. Writes serialize cooperating organization services by organization lock, then actor, class and target; full_clean validates changed records. Direct ORM bypass remains privileged; database races and user role/organization mutation protocols still require E08-05. Read querysets are request-scoped, not reusable authorization tokens. Future views must not serialize complete User objects.

## E05 / foundation carry-forward
E05-01 CI_PASSED; E05-02/03/04/05 IN_PROGRESS; E05-06 CI_PASSED with new control/manual checks open; E05-07 REVIEW at 666eee6; E05-08 TODO; E05-09 IN_PROGRESS; E05-10 TODO. E08-01 reported pass is not separate manual acceptance of E05, nor independently retrieved evidence for earlier runs. Staff accounts/passwords/MFA retained on deactivation; database-only revocation and no reactivation workflow.

E01–E03 partial, lockfile open. E04-02 bootstrap DONE; E04-01/03/04 CI_PASSED with security/manual gaps; E04-06 MFA recovery IN_PROGRESS; E04-05/07/08/09/10 recovery/last-owner/throttling/session work open. E06–E22 otherwise remain at preserved baseline. Python 3.14 support remains unverified.

## BUG-001
FIXED_VERIFIED. Bootstrap full_clean before set_password: owner 08:11 log had 50 tests, four errors, 46 passed. ef6b96c fixed ordering; owner reported passing rerun 08:24 EST. No migration.

## BUG-002
FIXED_VERIFIED. 1b4a5dd onboarding mail import corrected in e3bcfcb from django.contrib to django.core. Owner 13:21 log: 83 entries in 0.897s, one module-import error, 82 passed; no onboarding methods executed. Fourteen methods retained. Owner 13:28 message verified fworklow passed; no URL/count/logs, not independently retrieved. cd1f580 recorded report. No runtime/flag change.

## BUG-003
REVIEW, local fix owner-confirmed. 24453d6 changes no-referrer to same-origin, updates assertion and adds five CSRF methods retaining fourteen original methods. Owner reported invitation POST 403 at 14:39:31 with null origin; confirmed Fix worked 15:07 EST. Browser/version/full activation/deactivation results not supplied. Tests do not emulate browser header generation. Full manual acceptance and separately reported fix CI remain open; no CSRF bypass/null allowlisting. Internal token-path log redaction remains open.

## Historical commit evidence
1311cd3 config/CI and b3aca8d backend/guard included in later reported pass. ce49752 bootstrap corrected by ef6b96c. 031b843 association with earlier 50-test failure inferred. ef6b96c owner pass 08:24; d60ab7d owner pass 08:30; 0ce5595 owner pass 08:51. d4f9625 and cd1f580 no separately supplied CI results. 1b4a5dd historical failed log has no run SHA. e3bcfcb owner pass 13:28, URL/count unknown. 666eee6 and 24453d6 no separately reported runs; 6929d69 owner-reported pass with URL at 15:50. Current E08-02/03 CI PENDING; SHA assigned on commit. No unattended tracking automation; CI does not authorize launch.
