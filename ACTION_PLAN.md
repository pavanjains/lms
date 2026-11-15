# Robotics LMS — Action Plan

Updated: 2026-11-15, 13:43 EST. Repository: pavanjains/lms; main.

## Sources
[Ticket ledger](docs/TICKETS.md) is authoritative. [Onboarding notes](docs/E05_ONBOARDING.md) and [deactivation notes](docs/E05_DEACTIVATION.md) describe implementation. The ledger supersedes historical CI notes. Markdown IDs are not GitHub Issues; no background tracking automation is installed.

## Current increment
E05-07: owner-confirmed instructor deactivation, scoped authorization, retained account/credentials/MFA and database-session revocation. Fourteen tests authored. Status REVIEW; new CI and browser acceptance PENDING. No migration, runtime account action, real email or feature-flag activation.

Latest reported passing application commit: e3bcfcb, per owner's 13:28 EST confirmation. BUG-002 is FIXED_VERIFIED on that evidence; run URL/count not supplied and Actions not independently retrieved. Earlier onboarding commit 1b4a5dd failed on its test mail import (owner's 13:21 log: 83 entries, one error, no onboarding methods executed). Keep that history; do not infer new passing counts. cd1f580 records the passing report; no separate workflow result has been supplied for that documentation commit or this increment.

Staff authentication and onboarding remain disabled by default. Browser acceptance, operational approval and complete classroom LMS functionality remain open.

## Roadmap
| Epics | State |
|---|---|
| E01–E03 Foundations/data/shared UI | Partial; lockfile, formatter/setup and broader UI remain |
| E04 Staff identity/MFA | Partial; recovery, throttling and session limits remain |
| E05 Instructor lifecycle | Onboarding CI passed by owner report; E05-07 code pending CI/UAT; audit/delivery/concurrency remain |
| E06–E08 Student accounts/sessions/classes | TODO beyond baseline student models |
| E09–E12 Documents/lessons/assignments | TODO |
| E13–E17 Progress/feedback/workspaces/reports | TODO |
| E18–E20 Audit/deployment/recovery | TODO |
| E21 Full verification | Partial auth/onboarding inputs; deactivation tests pending; broader acceptance TODO |
| E22 Training/launch | TODO |

## Next actions
1. Verify E05-07 in CI and synthetic browser sessions; record actual evidence, not assumed counts.
2. Complete onboarding browser acceptance, PostgreSQL race tests and audit/delivery follow-ups.
3. Resolve password/activation throttling, session limits, recovery, token-path log redaction, approved mail origin/sender and delivery policy before operational enablement.
4. Implement E08 classes, shared instructors, enrollment and resource-scoped permissions.

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
