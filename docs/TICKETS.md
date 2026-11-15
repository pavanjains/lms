# Development Tickets and Fix Ledger

Updated: 2026-11-15, 13:43 EST. Parent: [ACTION_PLAN.md](../ACTION_PLAN.md).

## Rules and preserved baseline
TODO = not implemented; IN_PROGRESS = partial acceptance; REVIEW = authored code with CI/manual checks pending; CI_PASSED = included in reported/observed passing CI, with possible manual work remaining; DONE = scoped acceptance met; FIXED_VERIFIED = corrected with subsequent evidence.

[Preserved baseline ledger](https://github.com/pavanjains/lms/blob/cd1f5808a5144e47650eeed8392d8930d09a01bf/docs/TICKETS.md) retains earlier ticket references and history. No unaffected E01–E22 ticket is implicitly completed. E06–E22 ranges must be expanded before implementation. Markdown IDs are not GitHub Issues.

## Active E05 tickets
| Ticket | Status | Evidence / remaining work |
|---|---|---|
| E05-01 Invitation schema/services | CI_PASSED | d60ab7d, owner-reported pass |
| E05-02 Owner invite form | CI_PASSED | Owner-reported pass after e3bcfcb at 13:28 EST; browser acceptance pending |
| E05-03 Email delivery | IN_PROGRESS | Backend/rollback included in reported pass; transport approval and durable delivery/audit pending |
| E05-04 Acceptance | CI_PASSED | Reported pass after e3bcfcb; browser UAT pending |
| E05-05 Resend/revoke | CI_PASSED | Reported pass after e3bcfcb; manual UAT pending |
| E05-06 Instructor list/status | CI_PASSED | 0ce5595 passed per owner at 08:51 EST; manual UAT pending; new deactivation control awaits CI |
| E05-07 Deactivation | REVIEW | Scoped owner confirmation, inactive state, database-session revocation and fourteen tests authored; CI/UAT pending |
| E05-08 Concurrency | TODO | PostgreSQL simultaneous acceptance/reissue/revoke and deactivation/login tests |
| E05-09 Activation privacy/throttling | IN_PROGRESS | Header/filtering tests included in reported pass; log redaction and throttling pending |
| E05-10 Delivery reliability | TODO | Durable outbox/audit decision; ambiguous delivery handling |

[Onboarding implementation](E05_ONBOARDING.md) and [deactivation scope/manual checks](E05_DEACTIVATION.md). No tests executed in this authoring environment. No migration, runtime deactivation, real email or flag activation in the new E05-07 source increment. E05 remains open. Database sessions only; unsupported engines fail closed. Accounts, passwords, MFA and related records retained; reactivation not included.

## Foundation and staff carry-forward
E01–E03 remain partial per baseline; E01-03 lockfile is open. E04-02 bootstrap is DONE; E04-01/03/04 are CI_PASSED with manual/security gaps. E04-05 password recovery, E04-07 last-owner protection, E04-08 throttling, E04-09 approved session limits and E04-10 timeout tests remain open; E04-06 MFA recovery remains IN_PROGRESS. Owner MFA does not replace resource authorization.

## BUG-001 — Blank bootstrap password validation
Parent E04-02; FIXED_VERIFIED. Owner's 08:11 EST log: 50 tests, four bootstrap errors, remaining 46 passed. Cause: full_clean before set_password. ef6b96c corrects ordering; no migration. Owner reported passing rerun at 08:24 EST.

## BUG-002 — Onboarding test module cannot import mail
Parent E05-03 / E21. FIXED_VERIFIED based on owner's 13:28 EST passing-workflow confirmation after e3bcfcb. Introduced in 1b4a5dd; corrected in e3bcfcb.

Historical owner-supplied 13:21 EST log: 83 test entries in 0.897s, one module-import error and 82 passing entries. No onboarding methods executed in that failed run; the failed entry was unittest's module-load placeholder. Fix changes from django.contrib import mail to from django.core import mail. No methods removed/disabled, migration, runtime behavior change or flag activation.

Owner's verification message: "verified fworklow passed". Passing run URL/count/logs not supplied; Actions result not independently retrieved. No count inferred. Defect closure does not close browser acceptance, all E05 work or production gates.

## Commit / CI evidence
| Commit | Change | Evidence |
|---|---|---|
| 1311cd3 | Configuration/CI | Included in later reported pass |
| ce49752 | Bootstrap | Corrected by ef6b96c |
| b3aca8d | Backend/MFA guard | Included in later reported pass |
| 031b843 | MFA integration | Earlier 50-test failure; association inferred |
| ef6b96c | BUG-001 fix | Owner-reported pass 08:24 EST |
| d60ab7d | Invitation services | Owner-reported pass 08:30 EST |
| d4f9625 | Tracking docs | No separate result supplied |
| 0ce5595 | Owner list/revoke | Owner-reported pass 08:51 EST; URL/count unknown |
| 1b4a5dd | Onboarding | Historical 13:21 EST failed log; run SHA not supplied |
| e3bcfcb | BUG-002 fix | Owner-reported pass 13:28 EST; URL/count unknown |
| cd1f580 | Record BUG-002 verification | No separate workflow result supplied |
| Current E05-07 increment | Deactivation/session revocation/UI/tests/tracking | CI PENDING; SHA assigned at commit |

No inferred passing counts, independent Actions verification or unattended tracking automation. Historical feature notes do not override this ledger.
