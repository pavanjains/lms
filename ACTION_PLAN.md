# Robotics LMS — Action Plan

Last updated: 2026-11-15, 08:30 EST.
Repository: pavanjains/lms. Working branch: main.

## Tracking source of truth
- This file: roadmap, current milestone, next actions, and release gates.
- [Ticket ledger](docs/TICKETS.md): development tickets, fixes, status, and evidence.
- [Implementation summary](docs/IMPLEMENTATION_STATUS.md): concise current state.
- Feature documents explain implementation details; their historical verification notes do not override this ledger.
- docs/VALIDATION.json is a historical initial-slice artifact, not a current CI result.

There are no GitHub Issues as of this update. Ticket IDs below are Markdown tracking identifiers, not GitHub issue numbers. Earlier T001–T052 references are legacy parent scopes; use the E##-## identifiers for development tracking.

## Current state
Foundation, owner bootstrap, staff authentication/MFA integration, and instructor invitation backend services are committed. This is not a classroom-ready LMS.

Latest application commit: d60ab7d5cf1c21849549cfb5b3e1af5481cca76d — instructor invitation services.
Latest CI evidence: owner reported the latest workflow passed on 2026-11-15 at 08:30 EST, following that application commit. The run URL and latest test count were not supplied; the assistant has not independently retrieved the run.

Staff authentication remains disabled by default through LMS_STAFF_AUTH_ENABLED=false. Passing CI is not approval to enable production access. Invitation email delivery, screens, and public acceptance routes are not implemented.

## Epic roadmap
| Epic | Outcome | Status |
|---|---|---|
| E01 | Project and developer workflow | Partial: CI configured; dependency lock and independent setup pending |
| E02 | Configuration and data foundations | Partial: core models and decision register; configuration approvals pending |
| E03 | Shared UI components | Partial: minimal base layout only |
| E04 | Owner bootstrap and staff authentication | Partial: bootstrap complete; gated MFA integration committed; recovery/hardening pending |
| E05 | Instructor account lifecycle | Partial: invitation schema/services/tests; screens/email/deactivation UI pending |
| E06 | Student identity and credentials | Not started beyond baseline user/profile models |
| E07 | Shared-device student sessions | Not started |
| E08 | Classes, enrollment, authorization | Not started |
| E09 | Private document storage | Not started |
| E10 | Document validation and delivery | Not started |
| E11 | Lesson authoring/versioning | Not started |
| E12 | Assignments | Not started |
| E13 | Progress state/history | Not started |
| E14 | Instructor feedback | Not started |
| E15 | Instructor classroom workspace | Not started |
| E16 | Student learning experience | Not started |
| E17 | Reporting and CSV export | Not started |
| E18 | Audit and retention | Not started |
| E19 | Deployment and monitoring | Not started; CI alone is not deployment |
| E20 | Backup and recovery | Not started |
| E21 | End-to-end/security/capacity verification | Partial: automated authentication tests only; wider verification pending |
| E22 | Training and launch | Not started |

No implementation percentage is maintained without weighted estimates. Planning documents, generated code, passing tests, and production readiness are distinct measures.

## Next development batch
1. Complete E05-02/03/04: owner invitation screen, delivery integration, instructor activation form.
2. Complete E05-05: resend/revoke screens with clear delivery-failure behavior.
3. Add E05-08: PostgreSQL concurrency regression tests for simultaneous acceptance/reissue/revoke.
4. Complete E04 hardening before operational activation: password throttling, session limits, complete recovery tests and runbooks.
5. Begin E08 class schema, multiple-instructor membership, enrollment, and centralized class policies.

Owner invitation screens must require verified owner MFA. Activation must not permit role/organization selection or automatic staff access before MFA enrollment. Development email may use the configured console backend; real email requires an approved sender, origin, credentials, and delivery policy. Do not send real invitations merely to test this documentation update.

## Update protocol
For every future implementation/fix commit prepared through this workflow:
1. Reference the affected ticket or BUG ID in the commit message.
2. Update docs/TICKETS.md in the same commit: implemented scope, remaining work, tests, and status.
3. Update this file when roadmap, next actions, or release gates change.
4. Record CI as pending for the new code until evidence is available.
5. After CI evidence arrives, record the application SHA, conclusion, evidence source, and run URL/count when available.
6. A fix reopens the parent ticket if its acceptance is invalidated; close the BUG after verification without declaring the entire epic complete.
7. Record operational/manual tests separately from automated CI.

These are working rules for subsequent development, not an installed background agent. Markdown files do not update themselves. Creating or updating GitHub Issues is a separate external action requiring approval.

## Release gates
- [ ] Reviewed resolved dependency lockfile.
- [ ] Password-attempt throttling and approved idle/absolute session limits.
- [ ] Complete MFA/password recovery procedures and browser tests.
- [ ] Instructor onboarding, deactivation, and class-scoped access workflows.
- [ ] Student login and shared-device isolation.
- [ ] Lessons, private documents, assignments, progress, feedback.
- [ ] Audit, retention, privacy/consent, and center-device procedures approved.
- [ ] Staging deployment, monitoring, and database/document restore drill.
- [ ] Owner/instructor UAT and security/capacity verification.

## Commit history
| Commit | Change | Evidence |
|---|---|---|
| 1311cd3 | Restore hidden configuration and PostgreSQL CI | Committed |
| ce49752 | Owner bootstrap and ten tests | Initial bootstrap defect subsequently fixed |
| b3aca8d | Staff backend/MFA guard and sixteen tests | Included in later reported passing workflow |
| 031b843 | Gated MFA integration and fifteen tests | Included in later reported passing workflow |
| ef6b96c | BUG-001 bootstrap validation-order correction | Owner reported following workflow passed at 08:24 EST |
| d60ab7d | Invitation model/services/migration and seventeen tests | Owner reported latest workflow passed at 08:30 EST |
