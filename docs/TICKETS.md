# Development Tickets and Fix Ledger

Updated: 2026-11-15, 08:52 EST. Parent: [ACTION_PLAN.md](../ACTION_PLAN.md).

## Rules and preserved baseline
TODO = not implemented; IN_PROGRESS = partial acceptance; REVIEW = code with CI/manual checks pending; CI_PASSED = included in reported/observed passing CI with possible manual work remaining; DONE = scoped acceptance met; FIXED_VERIFIED = corrected with subsequent evidence.

[Full prior ticket ledger and reserved ticket ranges](https://github.com/pavanjains/lms/blob/0ce559556a1921d9b35a38915d231d53e1d4821d/docs/TICKETS.md) is the preserved baseline for all unaffected E01–E22 tickets. This file supersedes its E05/current-CI entries only; no other ticket is implicitly completed or removed. E06–E22 ranges must be expanded before their implementation. IDs are Markdown identifiers, not GitHub Issue numbers.

## Active E05 tickets
| Ticket | Status | Evidence / remaining work |
|---|---|---|
| E05-01 Invitation schema/services | CI_PASSED | d60ab7d, owner-reported pass |
| E05-02 Owner invite form | REVIEW | New confirmed form/MFA owner checks; CI and browser acceptance pending |
| E05-03 Email delivery | IN_PROGRESS | New backend integration and synchronous failure rollback; CI, real transport approval, durable delivery/audit pending |
| E05-04 Acceptance | REVIEW | New password-confirmation form; fixed instructor role/org; no automatic login; CI/UAT pending |
| E05-05 Resend/revoke | IN_PROGRESS | Revocation passed in 0ce5595 by owner report; new confirmed resend pending CI/UAT |
| E05-06 Instructor list/status | CI_PASSED | 0ce5595 passed per owner at 08:51 EST; manual UAT pending |
| E05-07 Deactivation | TODO | Administration/session invalidation workflow |
| E05-08 Concurrency | TODO | PostgreSQL simultaneous acceptance/reissue/revoke |
| E05-09 Activation privacy/throttling | IN_PROGRESS | New no-referrer/no-store and sensitive password filtering; token-path log redaction and throttling pending |
| E05-10 Delivery reliability | TODO | New follow-up: durable delivery audit/outbox decision; ambiguous SMTP/commit failure handling |

[Current implementation and manual checks](E05_ONBOARDING.md). Fourteen onboarding tests authored, not run in the authoring environment. Previous tests retained. No migration. No emails sent by this source commit. Onboarding/staff flags remain off. E05 is not complete.

## Foundation and staff carry-forward
E01–E03 remain partial per baseline. E01-03 lockfile is open. E04-02 bootstrap is DONE; E04-01/03/04 are CI_PASSED with manual/security gaps. E04-05 password recovery, E04-07 last-owner protection, E04-08 throttling, E04-09 approved session limits and E04-10 timeout tests remain open; E04-06 MFA recovery remains IN_PROGRESS. A verified owner is not exempt from class/resource policies.

## BUG-001 — Blank bootstrap password validation
Parent E04-02; FIXED_VERIFIED. Owner's 08:11 EST log: 50 tests, four bootstrap errors, remaining 46 passed. Cause: full_clean before set_password. ef6b96c corrects ordering; tests unchanged, no migration. Owner reported passing rerun at 08:24 EST.

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
| Current E05 onboarding increment | Invite/delivery/activation/resend + tracking | CI PENDING; SHA assigned at commit |

No latest count is inferred by adding authored tests. Passing CI reports are owner-provided, not independently retrieved. The new commit, including its documentation, requires its own verification. Historical feature documents do not override this evidence ledger.
