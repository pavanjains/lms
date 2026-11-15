# Development Tickets and Fix Ledger

Updated: 2026-11-15, 13:29 EST. Parent: [ACTION_PLAN.md](../ACTION_PLAN.md).

## Rules and preserved baseline
TODO = not implemented; IN_PROGRESS = partial acceptance; REVIEW = code with CI/manual checks pending; CI_PASSED = included in reported/observed passing CI with possible manual work remaining; DONE = scoped acceptance met; FIXED_VERIFIED = corrected with subsequent evidence.

[Full prior ticket ledger and reserved ticket ranges](https://github.com/pavanjains/lms/blob/0ce559556a1921d9b35a38915d231d53e1d4821d/docs/TICKETS.md) is the preserved baseline for all unaffected E01–E22 tickets. This file supersedes its E05/current-CI entries only; no other ticket is implicitly completed or removed. E06–E22 ranges must be expanded before their implementation. IDs are Markdown identifiers, not GitHub Issue numbers.

## Active E05 tickets
| Ticket | Status | Evidence / remaining work |
|---|---|---|
| E05-01 Invitation schema/services | CI_PASSED | d60ab7d, owner-reported pass |
| E05-02 Owner invite form | CI_PASSED | Included in owner-reported pass after e3bcfcb at 13:28 EST; browser acceptance pending |
| E05-03 Email delivery | IN_PROGRESS | Backend integration and rollback included in reported pass after e3bcfcb; real transport approval and durable delivery/audit pending |
| E05-04 Acceptance | CI_PASSED | Password confirmation, fixed instructor role/org and no automatic login included in reported pass after e3bcfcb; browser UAT pending |
| E05-05 Resend/revoke | CI_PASSED | Revocation previously passed by report; resend included in reported pass after e3bcfcb; manual UAT pending |
| E05-06 Instructor list/status | CI_PASSED | 0ce5595 passed per owner at 08:51 EST; manual UAT pending |
| E05-07 Deactivation | TODO | Administration/session invalidation workflow |
| E05-08 Concurrency | TODO | PostgreSQL simultaneous acceptance/reissue/revoke |
| E05-09 Activation privacy/throttling | IN_PROGRESS | Header/filtering tests included in reported pass after e3bcfcb; token-path log redaction and throttling pending |
| E05-10 Delivery reliability | TODO | Durable delivery audit/outbox decision; ambiguous SMTP/commit failure handling |

[Implementation and manual checks](E05_ONBOARDING.md); this ledger supersedes its historical CI-pending note. Fourteen onboarding tests authored. Owner confirmed passing workflow after e3bcfcb at 13:28 EST. Passing run count/URL not supplied; result not independently retrieved. E05 is not complete. No migration, real email execution or flag activation in this documentation update.

## Foundation and staff carry-forward
E01–E03 remain partial per baseline. E01-03 lockfile is open. E04-02 bootstrap is DONE; E04-01/03/04 are CI_PASSED with manual/security gaps. E04-05 password recovery, E04-07 last-owner protection, E04-08 throttling, E04-09 approved session limits and E04-10 timeout tests remain open; E04-06 MFA recovery remains IN_PROGRESS. A verified owner is not exempt from class/resource policies.

## BUG-001 — Blank bootstrap password validation
Parent E04-02; FIXED_VERIFIED. Owner's 08:11 EST log: 50 tests, four bootstrap errors, remaining 46 passed. Cause: full_clean before set_password. ef6b96c corrects ordering; tests unchanged, no migration. Owner reported passing rerun at 08:24 EST.

## BUG-002 — Onboarding test module cannot import mail
Parent E05-03 / E21. Status FIXED_VERIFIED based on owner-reported passing workflow after e3bcfcb at 13:28 EST. Introduced in 1b4a5dd; corrected in e3bcfcb.

Historical failure: owner supplied 13:21 EST log, Ran 83 tests in 0.897s, one import error, remaining 82 entries passed. The failed entry was unittest's module-load placeholder, not one of the fourteen onboarding methods; none of those methods executed in that failed run. Root cause: from django.contrib import mail. Correction: from django.core import mail. No test methods removed or disabled; no runtime application change, migration, flag activation or real email.

Verification evidence: owner's 13:28 EST message, "verified fworklow passed", in the context of the e3bcfcb fix. Passing run URL, exact test count and logs not supplied; Actions result not independently retrieved. No passing count inferred. This closes the import defect, not browser acceptance, E05 as a whole, or production release gates.

## Commit / CI evidence
| Commit | Change | Evidence |
|---|---|---|
| 1311cd3 | Configuration/CI | Included in later reported passing run |
| ce49752 | Bootstrap | Corrected by ef6b96c |
| b3aca8d | Backend/MFA guard | Included in later reported pass |
| 031b843 | MFA integration | Earlier 50-test failure; association inferred from conversation |
| ef6b96c | BUG-001 fix | Owner reported pass 08:24 EST |
| d60ab7d | Invitation services | Owner reported pass 08:30 EST |
| d4f9625 | Tracking documentation | No separate result supplied |
| 0ce5595 | Owner list/revoke | Owner reported pass 08:51 EST; URL/count unknown |
| 1b4a5dd | Invite/delivery/activation/resend + tracking | Historical owner-supplied 13:21 EST log: CI FAILED, onboarding import error; run SHA not supplied |
| e3bcfcb | BUG-002 mail import correction and tracking | CI_PASSED by owner report at 13:28 EST; URL/count unknown |
| Current documentation update | Record BUG-002 verification | Own CI PENDING; does not inherit e3bcfcb run result |

Passing CI reports are owner-provided, not independently retrieved. No latest count is inferred by adding authored tests. Historical feature documents do not override this evidence ledger. No unattended tracking automation is installed.
