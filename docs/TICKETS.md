# Development Tickets and Fix Ledger

Updated: 2026-11-15, 08:39 EST. Parent: [ACTION_PLAN.md](../ACTION_PLAN.md).

## Rules
TODO = not implemented; IN_PROGRESS = partial acceptance; REVIEW = code authored/committed with verification pending; CI_PASSED = included in reported/observed passing CI with other acceptance possibly open; DONE = scoped acceptance met; FIXED_VERIFIED = corrected defect with subsequent passing evidence.

Current passing CI evidence is owner-reported, not independently retrieved. Do not infer latest counts by adding authored tests. New changes start with CI PENDING. Markdown IDs are not GitHub Issue numbers. Legacy T001–T052 are parent scopes; retain E##-## for development.

## Active E05 increment
[Implementation/manual checks](E05_OWNER_MANAGEMENT.md).
- E05-05: revoke confirmation UI implemented; resend/delivery still missing. IN_PROGRESS; new code CI PENDING.
- E05-06: owner-only organization-scoped instructor/invitation lists, search, pagination, and statuses implemented. REVIEW; CI and manual UAT pending. Account changes/deactivation are not included.
- Fifteen owner-management tests authored; not run in the authoring environment.
- No new migration, real email, public acceptance, or feature-flag activation.

## Foundation
| Ticket | Status | Evidence / remaining work |
|---|---|---|
| E01-01 | CI_PASSED | Project bootstrap; no production deployment |
| E01-02 | IN_PROGRESS | Core/accounts/organizations only |
| E01-03 | IN_PROGRESS | Dependency declarations; resolved lockfile absent |
| E01-04 | CI_PASSED | Environment settings; deployment review remains |
| E01-05 | IN_PROGRESS | Compose exists; CI PostgreSQL passed by report; local walkthrough pending |
| E01-06 | IN_PROGRESS | Ruff lint gate; formatter gate pending |
| E01-07 | CI_PASSED | Pipeline in 1311cd3; new increment run pending |
| E01-08 | IN_PROGRESS | README; independent clean setup pending |
| E02-01 | IN_PROGRESS | Decision register; approvals remain |
| E02-02 | CI_PASSED | Organization/roles models |
| E02-03 | CI_PASSED | Custom user and first migration |
| E02-04 | CI_PASSED | Student profile; email optional; grade independent of kit |
| E02-05 | TODO | Timestamp/concurrency conventions |
| E02-06 | TODO | Operational migration/rollback policy |
| E02-07 | TODO | Reusable synthetic development fixtures |
| E03-01 | IN_PROGRESS | Base layout; MFA bridge; scoped owner pages added |
| E03-02–07 | TODO | Full shared navigation/components/errors; feature-specific components are partial inputs |

## Staff identity
| Ticket | Status | Evidence / remaining work |
|---|---|---|
| E04-01 | CI_PASSED | Established MFA integration; lockfile under E01-03 |
| E04-02 | DONE | Owner bootstrap; BUG-001 correction verified by owner-reported rerun |
| E04-03 | CI_PASSED | Email login/POST logout; flag off; browser UAT pending |
| E04-04 | CI_PASSED | TOTP enrollment/verification; boundary/browser checks remain |
| E04-05 | TODO | Password recovery |
| E04-06 | IN_PROGRESS | Recovery codes; full login/browser/runbook pending |
| E04-07 | TODO | Last-owner invariant and administration tests |
| E04-08 | TODO | Password throttling; release blocker |
| E04-09 | TODO | Approved staff idle/absolute limits; release blocker |
| E04-10 | TODO | Deterministic MFA timeout/expiry tests |

MFA guard does not replace class authorization. E04 stays open; staff authentication defaults off.

## Instructor lifecycle
| Ticket | Status | Evidence / remaining work |
|---|---|---|
| E05-01 | CI_PASSED | d60ab7d schema/token lifecycle; owner-reported pass |
| E05-02 | TODO | Owner invite form |
| E05-03 | TODO | Email sender/origin/configuration/failure policy |
| E05-04 | IN_PROGRESS | Acceptance service; public form/password confirmation/browser tests pending |
| E05-05 | IN_PROGRESS | Services and new revoke UI; resend/delivery pending; new CI pending |
| E05-06 | REVIEW | Instructor/invitation listing/status UI; CI/manual checks pending |
| E05-07 | TODO | Deactivation management workflow and session test |
| E05-08 | TODO | PostgreSQL simultaneous accept/reissue/revoke tests |
| E05-09 | TODO | Activation URL privacy/log redaction/throttling |

Only verified active owners manage invitations. Reissue invalidates old tokens; used/expired/revoked invitations fail; account failure does not consume a token; accepted users are always instructors in the invitation organization. New list/revoke pages reveal no raw tokens or digests. No create/send/activation UI is introduced by this increment.

## Later queues
Detailed rows must be expanded before implementation; reserved IDs retain the agreed breakdown.
| Epic | Reserved tickets | Scope/state |
|---|---|---|
| E06 | E06-01–08 | TODO student accounts |
| E07 | E07-01–08 | TODO student shared-device sessions |
| E08 | E08-01–11 | TODO classes/enrollment/policies |
| E09 | E09-01–06 | TODO private storage |
| E10 | E10-01–08 | TODO document validation/delivery |
| E11 | E11-01–10 | TODO lesson authoring/versioning |
| E12 | E12-01–10 | TODO assignments |
| E13 | E13-01–08 | TODO progress/concurrency |
| E14 | E14-01–06 | TODO feedback |
| E15 | E15-01–09 | TODO instructor workspace |
| E16 | E16-01–09 | TODO student lesson experience |
| E17 | E17-01–09 | TODO dashboards/exports |
| E18 | E18-01–08 | TODO audit/retention |
| E19 | E19-01–08 | TODO deployment/monitoring |
| E20 | E20-01–07 | TODO backups/restore |
| E21 | E21-01–09 | Full acceptance TODO; existing auth tests are partial inputs |
| E22 | E22-01–09 | TODO training/launch |

## BUG-001 — Bootstrap validates blank password
Parent E04-02. Status FIXED_VERIFIED.
Owner supplied 08:11 EST CI log: 50 tests, four bootstrap errors, remaining 46 passed. Cause: full_clean before password assignment. Fix ef6b96c validates password, hashes it, then validates/saves model. Tests unchanged; no migration. Owner reported passing rerun at 08:24 EST.

## Commit and CI history
| Commit | Change | Evidence |
|---|---|---|
| 1311cd3 | Hidden configuration/CI | Committed; included in subsequent reported passing run |
| ce49752 | Bootstrap and ten tests | Corrected by ef6b96c |
| b3aca8d | Staff backend/guard and sixteen tests | Included in subsequent reported passing run |
| 031b843 | Gated MFA integration and fifteen tests | 08:11 owner-pasted 50-test failure; commit association inferred from conversation |
| ef6b96c | BUG-001 correction | Owner reported passing workflow at 08:24 EST |
| d60ab7d | Invitation services and seventeen tests | Owner reported passing latest workflow at 08:30 EST; URL/count unknown |
| d4f9625 | Tracking documents | Committed; no separate CI result supplied |
| Current E05-05/E05-06 increment | Owner list/revoke and fifteen tests | CI PENDING; SHA assigned at commit |

Historical feature verification notes and VALIDATION.json do not override later evidence here. Update CI after evidence arrives; a documentation-only commit also has its own workflow result. No unattended tracking automation is installed.
