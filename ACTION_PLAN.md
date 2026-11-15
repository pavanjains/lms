# Robotics LMS — Action Plan

Updated: 2026-11-15, 13:29 EST. Repository: pavanjains/lms; main.

## Sources
[Ticket ledger](docs/TICKETS.md) is authoritative. [Onboarding notes](docs/E05_ONBOARDING.md) describe implementation; the ledger supersedes their historical CI-pending note. Earlier feature notes and VALIDATION.json are historical. Markdown IDs are not GitHub Issues and no background automation updates them.

## Current increment
E05-02/03/04/05: owner invite form, configured-backend email, one-time activation, confirmed resend (1b4a5dd). Fourteen onboarding tests authored. BUG-002 corrected the test mail import in e3bcfcb. Status FIXED_VERIFIED based on the owner's 13:28 EST confirmation that the workflow passed after e3bcfcb. Onboarding now has owner-reported passing-CI evidence; browser acceptance and production approval remain open. No passing test count or run URL supplied; Actions result not independently retrieved.

Historical failure retained: owner-supplied 13:21 EST log showed 83 test entries and one onboarding module-import error; onboarding test methods did not execute in that failed run. The later passing report supersedes that failure as the latest reported result, not as a deletion of its history.

Both staff access and instructor onboarding remain disabled by default. New instructor activation does not log the user in; subsequent sign-in requires MFA enrollment. This documentation-only update changes no application code, migrations, mail settings, credentials or flags. Its own workflow result is pending and is separate from the reported pass for e3bcfcb. The classroom LMS is not complete.

## Roadmap
| Epics | State |
|---|---|
| E01–E03 Foundations/data/shared UI | Partial; lockfile, formatter/setup checks and broader UI remain |
| E04 Staff identity/MFA | Partial; recovery, throttling, session limits remain |
| E05 Instructor lifecycle | In progress; onboarding CI passed by owner report after e3bcfcb; deactivation/audit/concurrency/UAT remain |
| E06–E08 Student accounts/sessions/classes | TODO beyond baseline student models |
| E09–E12 Documents/lessons/assignments | TODO |
| E13–E17 Progress/feedback/workspaces/reports | TODO |
| E18–E20 Audit/deployment/recovery | TODO |
| E21 Full verification | Partial auth/onboarding tests only; broader acceptance TODO |
| E22 Training/launch | TODO |

## Next actions
1. Complete local/staging onboarding browser acceptance using synthetic mail; record evidence separately from CI. Attach run URL/count if supplied, without inferring counts.
2. Complete E05 deactivation, PostgreSQL race tests, audit/delivery follow-ups and browser UAT.
3. Resolve password/activation throttling, session limits, recovery, token-path log redaction, approved mail origin/sender and delivery policy before operational enablement.
4. Implement E08 classes, shared instructors, enrollment and resource-scoped permissions.

## Update protocol
Every implementation/fix commit references ticket/BUG IDs and updates the ledger. New CI starts PENDING. Distinguish owner-reported CI from direct observations; do not infer counts. Preserve bug history, reopen invalidated acceptance, and record manual tests separately. CI is not production authorization.

## Release gates
- [ ] Reproducible dependencies/setup.
- [ ] Auth/activation throttling, sessions and recovery.
- [ ] Complete instructor lifecycle and class permissions.
- [ ] Student access/shared-device isolation.
- [ ] Lessons/documents/assignments/progress/feedback/reporting.
- [ ] Audit, privacy/consent, retention and device procedures.
- [ ] Deployment/monitoring/database-document restore.
- [ ] Browser UAT, security/capacity acceptance and training.
