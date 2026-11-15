# Development Tickets and Fix Ledger

Last updated: 2026-11-15, 08:30 EST.
Parent roadmap: [ACTION_PLAN.md](../ACTION_PLAN.md).

## Status rules
- TODO: not implemented.
- IN_PROGRESS: partial implementation, with remaining acceptance stated.
- CI_PASSED: scoped code committed and included in an owner-reported or directly observed passing run; other acceptance may remain.
- DONE: scoped acceptance met with evidence; does not imply epic or production readiness.
- BLOCKED: cannot proceed until a named dependency or decision is resolved.
- FIXED_VERIFIED: defect fixed and a subsequent passing run reported/observed.

Evidence source must be explicit. Current CI confirmations are owner-reported in conversation, not independently retrieved Actions results. Latest run count and URL are unknown. Do not infer that the suite has 67 passing tests simply by adding authored test counts.

## Foundation and UI
| Ticket | Scope | Status | Evidence / remaining acceptance |
|---|---|---|---|
| E01-01 | Django project bootstrap | CI_PASSED | Project committed and covered by reported CI; no production deployment |
| E01-02 | Application module structure | IN_PROGRESS | core/accounts/organizations exist; remaining feature modules later |
| E01-03 | Dependency management and lock | IN_PROGRESS | Ranges plus selected MFA release; resolved lockfile missing |
| E01-04 | Environment settings | CI_PASSED | Development/test/CI/production authored; hosting safeguards require deployment review |
| E01-05 | Local PostgreSQL setup | IN_PROGRESS | Compose authored; CI PostgreSQL reported passing; independent local setup not demonstrated |
| E01-06 | Lint/format tools | IN_PROGRESS | Ruff lint in reported passing CI; formatter gate pending |
| E01-07 | Automated pipeline | CI_PASSED | Workflow committed in 1311cd3; latest pass reported by owner |
| E01-08 | Developer setup guide | IN_PROGRESS | README exists; clean-checkout walkthrough pending |
| E02-01 | Configuration register | IN_PROGRESS | DECISIONS.md exists; several approvals unresolved |
| E02-02 | Organization and roles | CI_PASSED | Models/migrations present in passing suite |
| E02-03 | Custom user model | CI_PASSED | Initial migration present; staff backend integrated |
| E02-04 | Student profile/grade | CI_PASSED | Email optional; grade independent of kit; no onboarding UI |
| E02-05 | Timestamp/concurrency conventions | TODO | Define before assignment/progress implementation |
| E02-06 | Migration/rollback policy | TODO | CI drift checks exist; operational policy not written |
| E02-07 | Development fixtures | TODO | Synthetic tests are not a reusable development fixture set |
| E03-01 | Shared base layout | IN_PROGRESS | Minimal layout and MFA template bridge only |
| E03-02–07 | Navigation/components/error states | TODO | Full role navigation, forms, tables, dialogs, and error UX pending |

## Owner and staff authentication
| Ticket | Scope | Status | Evidence / remaining acceptance |
|---|---|---|---|
| E04-01 | Integrate established auth components | CI_PASSED | b3aca8d and 031b843; gated integration included in reported pass; dependency lock pending under E01-03 |
| E04-02 | Initial owner bootstrap | DONE | ce49752, corrected by ef6b96c; owner reported passing rerun; existing accounts not overwritten |
| E04-03 | Staff sign-in/logout | CI_PASSED | Email backend and POST logout integrated; feature flag off; browser UAT pending |
| E04-04 | MFA enrollment/verification | CI_PASSED | Authenticator setup and real-token tests authored/included in reported pass; timeout/clock-boundary/browser checks pending |
| E04-05 | Staff password recovery | TODO | No password-reset flow implemented |
| E04-06 | MFA recovery | IN_PROGRESS | Library recovery codes integrated; full recovery-login browser test/runbook pending |
| E04-07 | Last-owner protection | TODO | No owner-management UI; explicit invariant/service tests pending |
| E04-08 | Password attempt throttling | TODO | Added security follow-up; release blocker |
| E04-09 | Staff idle/absolute session limits | TODO | Added security follow-up; values need approval |
| E04-10 | MFA timeout/expiry regressions | TODO | Added security follow-up; deterministic time tests required |

The MFA guard is an access prerequisite, not class-level authorization. Staff authentication stays disabled by default. Do not mark E04 complete while recovery/hardening remains.

## Instructor onboarding
| Ticket | Scope | Status | Evidence / remaining acceptance |
|---|---|---|---|
| E05-01 | Invitation schema and token lifecycle | CI_PASSED | d60ab7d; migration and digest-only storage; reported passing workflow |
| E05-02 | Owner invitation form | TODO | Verified-owner screen and validation required |
| E05-03 | Invitation email delivery | TODO | Approved origin/sender, backend configuration, failure policy required |
| E05-04 | Invitation acceptance | IN_PROGRESS | One-time acceptance service complete; public form, password confirmation, CSRF and browser tests pending |
| E05-05 | Resend/revoke | IN_PROGRESS | Services committed; owner controls and delivery integration pending |
| E05-06 | Instructor list/status controls | TODO | No owner-facing account list yet |
| E05-07 | Instructor deactivation UI/workflow | TODO | Backend rejects inactive staff; management workflow and end-to-end session test pending |
| E05-08 | Invitation concurrency regressions | TODO | Added follow-up; PostgreSQL simultaneous accept/reissue/revoke tests |
| E05-09 | Activation URL privacy/throttling | TODO | Added follow-up; referrer policy, log redaction, rate limits |

Invitation service behavior implemented: active verified owner required; replacement revokes old pending tokens; accepted/expired/revoked tokens rejected; account failures preserve unused invitation; new account always INSTRUCTOR in the specified organization. No emails or public invitation routes are enabled.

## Later epic queues
The E06–E22 ticket IDs retain the previously agreed breakdown. Their detailed rows must be added before implementation, using these reserved ranges; they are not GitHub Issues.

| Epic | Reserved tickets | Current state |
|---|---|---|
| E06 | E06-01–08 | TODO: student identities, onboarding, reset, disable |
| E07 | E07-01–08 | TODO: student shared-device sessions |
| E08 | E08-01–11 | TODO: classes, membership, enrollment, policies |
| E09 | E09-01–06 | TODO: private object storage |
| E10 | E10-01–08 | TODO: document validation/delivery |
| E11 | E11-01–10 | TODO: lesson authoring/versioning |
| E12 | E12-01–10 | TODO: assignments/lifecycle |
| E13 | E13-01–08 | TODO: progress/history/concurrency |
| E14 | E14-01–06 | TODO: instructor feedback |
| E15 | E15-01–09 | TODO: instructor workspace/bulk progress |
| E16 | E16-01–09 | TODO: student lesson experience |
| E17 | E17-01–09 | TODO: calculations/dashboards/exports |
| E18 | E18-01–08 | TODO: audit/retention |
| E19 | E19-01–08 | TODO: staging/production/monitoring |
| E20 | E20-01–07 | TODO: backups/restore |
| E21 | E21-01–09 | TODO for full acceptance; authentication tests are partial inputs |
| E22 | E22-01–09 | TODO: training/procedures/launch |

## Fix history
### BUG-001 — Bootstrap validates blank password
- Parent: E04-02.
- Status: FIXED_VERIFIED.
- Observed: owner supplied CI output on 2026-11-15 at 08:11 EST: 50 tests, 4 bootstrap errors; remaining 46 passed.
- Cause: owner.full_clean() executed before owner.set_password().
- Fix: ef6b96c89b474bd3919e0b7c33e732cd535df370 validates password, hashes it, then validates/saves model.
- Regression evidence: original tests retained; owner reported workflow passed at 08:24 EST.
- No migration required; no assertions weakened.

## CI evidence ledger
| Application SHA | Evidence time (EST) | Result | Source / limits |
|---|---|---|---|
| 031b843 | 2026-11-15 08:11 | Failed: 50 tests, 4 errors | Owner-pasted runtime log; commit association based on conversation |
| ef6b96c | 2026-11-15 08:24 | Passed | Owner report after bootstrap fix; run URL not supplied |
| d60ab7d | 2026-11-15 08:30 | Passed | Owner report of latest workflow; count/run URL not supplied |

After each new code commit, its CI result begins PENDING even if an earlier commit passed. A documentation-only change also has a separate workflow run; do not claim its result in advance.
