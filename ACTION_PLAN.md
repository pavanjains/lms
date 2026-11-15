# Robotics LMS — Action Plan

Updated: 2026-11-15, 15:09 EST. Repository: pavanjains/lms; main.

## Sources
[Ticket ledger](docs/TICKETS.md) is authoritative. [Onboarding notes](docs/E05_ONBOARDING.md) and [deactivation notes](docs/E05_DEACTIVATION.md) describe implementation. The ledger supersedes historical CI notes. Markdown IDs are not GitHub Issues; no background tracking automation is installed.

## Current increment
BUG-003: onboarding form responses now use Referrer-Policy same-origin instead of no-referrer. The existing privacy-header assertion is updated; five CSRF-enforced regression methods cover same-origin invitation/resend/activation and rejection of null/cross-origin invitation/activation requests. All fourteen original onboarding test methods remain. Tests authored, NOT RUN here; CI PENDING. Owner confirmed the one-line local fix worked at 15:07 EST; complete activation and deactivation browser acceptance are not implied. No migration, feature-flag change, real email or runtime account action.

E05-07 remains REVIEW at 666eee6: owner-confirmed instructor deactivation, scoped authorization, retained account/credentials/MFA and database-session revocation. Fourteen deactivation tests authored; CI and browser acceptance PENDING.

Latest reported passing application commit remains e3bcfcb, per owner's 13:28 EST confirmation. BUG-002 is FIXED_VERIFIED on that evidence; run URL/count not supplied and Actions not independently retrieved. Earlier onboarding commit 1b4a5dd failed on its test mail import (owner's 13:21 log: 83 entries, one error, no onboarding methods executed). Keep that history; do not infer new passing counts. cd1f580 records the passing report; no separate workflow result has been supplied for that documentation commit or later increments.

Staff authentication and onboarding remain disabled by default. Browser acceptance, operational approval and complete classroom LMS functionality remain open. Python 3.14 local constraint edits are not yet repository support or CI verification.

## Roadmap
| Epics | State |
|---|---|
| E01–E03 Foundations/data/shared UI | Partial; lockfile, formatter/setup and broader UI remain |
| E04 Staff identity/MFA | Partial; recovery, throttling and session limits remain |
| E05 Instructor lifecycle | Earlier onboarding CI passed by owner report; BUG-003 local fix reported working; new fix/deactivation CI pending |
| E06–E08 Student accounts/sessions/classes | TODO beyond baseline student models; E08 first increment scoped below |
| E09–E12 Documents/lessons/assignments | TODO |
| E13–E17 Progress/feedback/workspaces/reports | TODO |
| E18–E20 Audit/deployment/recovery | TODO |
| E21 Full verification | Partial auth/onboarding inputs; new origin/deactivation tests pending; broader acceptance TODO |
| E22 Training/launch | TODO |

## Next actions
1. Run BUG-003 regression/full PostgreSQL CI and browser invitation/resend/activation checks; preserve owner-reported evidence separately.
2. Verify E05-07 in CI and synthetic browser sessions; record actual evidence, not assumed counts.
3. Start E08-01 through E08-03 as a separate implementation increment: class/membership schema and migrations, transactional validated services, centralized scoped query policies and tests. No class UI or student sign-in claimed by this fix.
4. Complete onboarding PostgreSQL race tests and audit/delivery follow-ups.
5. Resolve password/activation throttling, session limits, recovery, token-path log redaction, approved mail origin/sender and delivery policy before operational enablement.
6. Review Python 3.14 dependency resolution and add CI coverage before declaring support.

## Update protocol
Every implementation/fix commit references ticket/BUG IDs and updates all three tracking documents. New CI starts PENDING; owner-reported CI and direct observations stay distinct. Preserve bug history, reopen invalidated acceptance, and record manual tests separately. CI is not production authorization.

## Release gates
- [ ] Reproducible dependencies/setup.
- [ ] Auth/activation throttling, sessions and recovery.
- [ ] Complete instructor lifecycle and class permissions.
- [ ] Student access/shared-device isolation.
- [ ] Lessons/documents/assignments/progress/feedback/reporting.
- [ ] Audit, privacy/consent, retention and device procedures.
- [ ] Deployment/monitoring/database-document restore.
- [ ] Browser UAT, security/capacity acceptance and training.
