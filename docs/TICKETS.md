# Development Tickets and Fix Ledger

Updated: 2026-11-15, 15:19 EST. Parent: ../ACTION_PLAN.md.

## Rules and preserved history
TODO = not implemented; IN_PROGRESS = partial; REVIEW = authored code awaiting verification; CI_PASSED = passing evidence with possible manual work remaining; DONE = scoped acceptance met; FIXED_VERIFIED = correction with subsequent evidence. Owner-reported and independently observed results remain distinct.

[Complete preceding ledger at 24453d6](https://github.com/pavanjains/lms/blob/24453d623785f1ff560c3444bcb5eedbb564a36c/docs/TICKETS.md) preserves ticket ranges, commit evidence and full BUG history; [earlier baseline](https://github.com/pavanjains/lms/blob/cd1f5808a5144e47650eeed8392d8930d09a01bf/docs/TICKETS.md) preserves earlier E01–E22 references. No unaffected ticket is completed implicitly. Markdown IDs are not GitHub Issues.

## E08 classrooms
| Ticket | State | Scope / evidence |
|---|---|---|
| E08-01 | REVIEW | apps/classrooms models, migration, registration and tests authored. CI, migration execution and drift checks PENDING. |
| E08-02 | TODO | Transactional validated class/membership/enrollment services; fresh actor and MFA checks; repeat-safe changes. |
| E08-03 | TODO | Organization/class/student visibility policies and isolation tests. Shared student does not expose other class records. |
| E08-04 | TODO | MFA/CSRF-protected class and membership UI; browser acceptance. |
| E08-05 | TODO | PostgreSQL concurrency and shared-instructor end-to-end acceptance. |

See CLASSROOMS.md for boundaries. E08-01 only creates schema on later migration execution; no accounts/data seeded or existing users rewritten. Model clean validation is not authorization and is bypassed by raw ORM writes. Services/policies must precede routes. No new flags or Python metadata changes. Tests authored, not executed here; no passing count inferred.

## E05 carry-forward
| Ticket | State | Evidence / remaining work |
|---|---|---|
| E05-01 | CI_PASSED | d60ab7d owner-reported pass. |
| E05-02 | IN_PROGRESS | Earlier e3bcfcb owner-reported pass; BUG-003 local correction confirmed, new CI/browser acceptance pending. |
| E05-03 | IN_PROGRESS | Backend/rollback in earlier reported pass; approved transport, durable delivery/audit pending. |
| E05-04 | IN_PROGRESS | Earlier reported pass; BUG-003 shared-header fix committed, activation browser/new CI pending. |
| E05-05 | IN_PROGRESS | Earlier reported pass; resend header regression fixed, new CI/manual acceptance pending. |
| E05-06 | CI_PASSED | 0ce5595 owner-reported pass 08:51 EST; manual UAT and new deactivation control CI pending. |
| E05-07 | REVIEW | 666eee6 deactivation/session revocation, fourteen authored tests; CI/UAT pending. |
| E05-08 | TODO | PostgreSQL accept/reissue/revoke and login/deactivation races. |
| E05-09 | IN_PROGRESS | BUG-003 header/tests authored; CI, log redaction and throttling pending. |
| E05-10 | TODO | Outbox/audit decision and ambiguous delivery handling. |

Database-only session revocation; accounts/passwords/MFA retained, reactivation not included. E05 remains open.

## Foundation / staff carry-forward
E01–E03 partial; E01-03 lockfile open. E04-02 bootstrap DONE. E04-01/03/04 CI_PASSED with manual/security gaps. E04-05 password recovery, E04-07 last-owner protection, E04-08 throttling, E04-09 session limits and E04-10 timeout tests open. E04-06 MFA recovery IN_PROGRESS. E06–E22 otherwise remain at preserved baseline; expand tickets before implementation. Python 3.14 local edits are not repository/CI verification.

## BUG-001 — Blank bootstrap password validation
FIXED_VERIFIED; parent E04-02. Owner 08:11 EST log: 50 tests, four errors, 46 passed. Cause full_clean before set_password; ef6b96c corrects ordering without migration. Owner reported passing rerun 08:24 EST.

## BUG-002 — Onboarding test mail import
FIXED_VERIFIED; parent E05-03/E21. Introduced 1b4a5dd; e3bcfcb changes django.contrib mail to django.core mail. Owner 13:21 EST failure log: 83 entries in 0.897s, one module-import error, 82 passing entries; no onboarding methods executed. Fourteen onboarding methods retained. Owner 13:28 EST message: verified fworklow passed. Passing URL/count/logs unavailable; not independently retrieved. No passing count inferred; no migration, runtime or flag change.

## BUG-003 — Onboarding null-origin browser POST
REVIEW; parent E05-02/04/05/09/E21. Committed 24453d6. Owner reported POST /staff/owner/invitations/new/ 403 at 14:39:31, Origin checking failed - null does not match any trusted origins. Shared page header no-referrer changed to same-origin; owner confirmed Fix worked at 15:07 EST. Browser/version and full activation/deactivation results not supplied.

Existing privacy assertion updated, five CSRF-enforced methods added; fourteen original methods retained. Same-origin invite/resend/activation success and null/cross-origin invite/activation rejection covered by authored tests, NOT RUN here. Tests do not simulate browser header generation. New CI/browser acceptance pending; no CSRF bypass/null allowlisting. Internal Referer token paths still require log redaction. No migration or flag change.

## Commit / CI evidence
1311cd3 config/CI, b3aca8d backend/MFA guard included in later reported pass. ce49752 bootstrap corrected by ef6b96c. Earlier 031b843 association with 50-test failure inferred. ef6b96c passed per owner 08:24 EST; d60ab7d passed per owner 08:30; 0ce5595 passed per owner 08:51. d4f9625 and cd1f580 documentation commits have no separately supplied results. 1b4a5dd failed per historical 13:21 log (run SHA not supplied); e3bcfcb passed per owner 13:28, URL/count unknown. 666eee6 and 24453d6 CI pending. Current E08-01 CI pending; SHA assigned at commit.

No independently retrieved Actions verification or unattended tracking automation. CI does not close production/manual gates.
