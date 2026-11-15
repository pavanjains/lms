# Robotics LMS — Action Plan

Updated: 2026-11-15, 13:21 EST. Repository: pavanjains/lms; main.

## Sources
[Ticket ledger](docs/TICKETS.md) is authoritative. [Onboarding notes](docs/E05_ONBOARDING.md) cover the current increment. Earlier feature notes and VALIDATION.json are historical. Markdown IDs are not GitHub Issues and no background automation updates them.

## Current increment
E05-02/03/04/05: owner invite form, configured-backend email, one-time activation, confirmed resend (1b4a5dd). Fourteen tests authored. CI FAILED by owner-supplied 13:21 EST log: onboarding module import error; 83 test entries, one error. No onboarding test method executed. BUG-002 corrects django.contrib mail import to django.core; fix CI PENDING. No migration, real email execution, production credentials, or feature activation.

Latest previously reported passing application commit: 0ce5595 (owner reported 08:51 EST). Run URL/count not supplied; result not independently retrieved. E05-06 is CI_PASSED with manual UAT pending; E05-05 revocation passed but new resend awaits CI.

Both staff access and instructor onboarding remain disabled by default. New instructor activation does not log the user in; subsequent sign-in requires MFA enrollment. The classroom LMS is not complete.

## Roadmap
| Epics | State |
|---|---|
| E01–E03 Foundations/data/shared UI | Partial; lockfile, formatter/setup checks and broader UI remain |
| E04 Staff identity/MFA | Partial; recovery, throttling, session limits remain |
| E05 Instructor lifecycle | In progress; onboarding CI failed; BUG-002 fix pending CI; deactivation/audit/concurrency/UAT remain |
| E06–E08 Student accounts/sessions/classes | TODO beyond baseline student models |
| E09–E12 Documents/lessons/assignments | TODO |
| E13–E17 Progress/feedback/workspaces/reports | TODO |
| E18–E20 Audit/deployment/recovery | TODO |
| E21 Full verification | Partial auth tests only; broader acceptance TODO |
| E22 Training/launch | TODO |

## Next actions
1. Run CI after BUG-002, including onboarding discovery and execution; record actual counts and any further failures. Then verify local/staging with synthetic mail.
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
