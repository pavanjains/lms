# Implementation Status

Updated: 2026-11-15, 15:50 EST. Ticket evidence: docs/TICKETS.md.

## Current E08-02/E08-03 increment
Transactional services implement owner class creation/archive, instructor assignment/removal, and owner/assigned-instructor enrollment management. Current actor is reloaded, organization active state checked, staff feature flag and callable MFA verification required. Writes lock organization, actor, class and target; changed models run full_clean. Adds/reactivations preserve unique relationship rows; repeated removals/archives are safe. Instructor enrollment requires existing student visibility.

Policies return organization-scoped classes, active eligible students and authorized class rosters. Owners can list archived classes; instructors see only active assigned classes. Shared student visibility never grants another class. Read querysets must be used immediately within a request, not cached/reused as authorization. Full User objects must not be serialized by future views.

Tests authored, NOT RUN here; new CI pending. No migration, route/UI, account creation, student login, audit schema, real email or flag activation. Permission services are not a complete student-onboarding solution: initial instructor access for newly created students remains future work. Concurrent raw ORM writes and role/organization mutations are outside the cooperating organization lock protocol; PostgreSQL concurrency acceptance pending.

## E08-01 verification
6929d69 app/schema/migration/model tests: CI_PASSED by owner report at 15:50 EST. Supplied run https://github.com/pavanjains/lms/actions/runs/43758274124 could not be fetched; not independently verified. Count/logs unavailable; no count inferred. Local database migration/browser acceptance not implied.

## Existing / history
[Previous implementation status](https://github.com/pavanjains/lms/blob/6929d69be5d009831588712694b43a3238006e32/docs/IMPLEMENTATION_STATUS.md) preserves all preceding slices and limitations. Organization/user/profile foundation, owner bootstrap, staff backend/MFA/workspace, invitations/activation, management/revoke, deactivation and origin-header correction remain implemented.

BUG-001 and BUG-002 retain FIXED_VERIFIED based on owner evidence. Historical BUG-002 failure: 83 entries, one import error, 82 passed, no onboarding methods executed; later e3bcfcb pass owner-confirmed 13:28 without count. BUG-003 local fix owner-confirmed 15:07; full browser acceptance pending. E05-07 manual session-deactivation acceptance also pending. New E08 tests not covered by prior reported passes.

## Next / operational limits
E08-04 class UI and E08-05 races/browser tests next. No current classroom browser routes. Model save/bulk operations can bypass full_clean; no row-level security/triggers. Memberships retained after account/class deactivation; policies must check current statuses. Kit selection stays with future lessons/assignments, not fixed on classes.

Student creation/access/shared-device isolation, lessons/documents/assignments, progress/feedback/reports, deployment/restore/monitoring, recovery/throttling/last-owner/session controls, audit, approved mail/delivery, token-log redaction and privacy/retention/training remain open. Python 3.14 support remains unverified. Staff flags remain off by default; CI is not production approval.
