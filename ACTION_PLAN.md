# Robotics LMS — Action Plan

Updated: 2026-11-15, 08:39 EST. Repository: pavanjains/lms; branch: main.

## Progress tracking
- [Ticket ledger](docs/TICKETS.md): authoritative ticket and fix statuses.
- [Current E05 increment](docs/E05_OWNER_MANAGEMENT.md): implementation and manual acceptance steps.
- docs/IMPLEMENTATION_STATUS.md summarizes earlier baseline work; this plan and the ledger govern later increments.
- docs/VALIDATION.json remains a historical initial-slice artifact.
- IDs are Markdown tickets, not GitHub Issues. No background automation updates them.

## Current increment
E05-05/E05-06: owner instructor/invitation listing and confirmed invitation revocation. Code and fifteen tests authored; CI PENDING for this commit. No migration, email, public acceptance, or production activation.

Latest previously reported passing application commit: d60ab7d (owner confirmation, 08:30 EST). Its run URL/count were not supplied. No CI result is claimed for the new increment or preceding documentation-only commit.

Staff authentication remains disabled by default. CI success is not production authorization. Owner bootstrap, staff MFA, and invitation backend services are committed; the classroom LMS is not complete.

## Epic roadmap
| Epic | State |
|---|---|
| E01 Project/workflow | Partial: lockfile, formatter gate, independent setup remain |
| E02 Data/configuration | Partial: core models exist; policies/approvals remain |
| E03 Shared UI | Partial: basic layout and scoped owner UI only |
| E04 Staff identity/MFA | Partial: recovery and hardening remain |
| E05 Instructor lifecycle | In progress: backend plus owner list/revoke; CI pending for UI |
| E06 Student accounts | TODO beyond initial user/profile models |
| E07 Student shared-device sessions | TODO |
| E08 Classes/enrollment/authorization | TODO |
| E09 Private storage | TODO |
| E10 Document validation/delivery | TODO |
| E11 Lessons/versioning | TODO |
| E12 Assignments | TODO |
| E13 Progress/history | TODO |
| E14 Feedback | TODO |
| E15 Instructor workspace | TODO |
| E16 Student lesson UI | TODO |
| E17 Reports/exports | TODO |
| E18 Audit/retention | TODO |
| E19 Deployment/monitoring | TODO; CI is not deployment |
| E20 Backup/recovery | TODO |
| E21 Full acceptance/security/capacity | Partial authentication inputs only |
| E22 Training/launch | TODO |

## Next actions
1. Verify owner list/revoke increment in CI and local/staging browser walkthrough.
2. Implement E05-02/03/04 invite form, delivery, and instructor activation; E05-05 resend.
3. Implement E05-07 deactivation and E05-08 PostgreSQL concurrency regressions.
4. Complete E04 password throttling, approved idle/absolute limits, recovery and timeout tests before operational activation.
5. Start E08 class schema, shared teaching, enrollment, and class-level policies.

No actual invitation email is sent by this increment. Real delivery requires an approved origin/sender, credentials, and retry/failure policy. Activation must not permit arbitrary role/organization selection or bypass MFA.

## Update rules
Every future code/fix commit must reference ticket/BUG IDs and update the ledger in the same change. New CI starts PENDING. Record SHA, source, conclusion, and URL/count when available. Reopen affected acceptance when a defect invalidates it. CI evidence and manual/operational evidence are separate. Do not claim production readiness from unit tests or invent a weighted completion percentage.

## Release gates
- [ ] Reviewed dependency lockfile and repeatable setup.
- [ ] Auth throttling, session limits, recovery and browser checks.
- [ ] Instructor onboarding/deactivation and class-scoped authorization.
- [ ] Student access and shared-device isolation.
- [ ] Lessons/documents/assignments/progress/feedback.
- [ ] Audit, retention, privacy/consent, center procedures.
- [ ] Deployment, monitoring, database/document restore drill.
- [ ] Owner/instructor UAT and security/capacity acceptance.

Commit/evidence history is preserved in docs/TICKETS.md. Full operational implementation remains pending.
