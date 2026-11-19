# Implementation Status

Updated: 2026-11-18, 20:09 EST. docs/TICKETS.md tracks evidence.

## E08-05 concurrency portion authored
PostgreSQL TransactionTestCase suite uses two worker connections and main observer, distinct backend PIDs, real service calls, uncommitted leader transaction and pg_blocking_pids-confirmed follower wait. Tests cover duplicate class/relationship writes, removal/archive/deactivation ordering against enrollment, and end/re-enrollment row reuse. Expected permission/validation failures asserted; SQL/worker failures propagate. Thread connections close and waits bounded.

CI requires PostgreSQL before the existing full suite and bounds job duration. SQLite explicitly skips the concurrency class. Tests authored, NOT RUN here; CI PENDING. E08-05 stays IN_PROGRESS because browser/shared-instructor acceptance is separate. No runtime code behavior, migration, schema, seed accounts, real data/email or feature-flag changes.

## Prior increments / evidence
[Complete previous status](https://github.com/pavanjains/lms/blob/d437edf410412d40e9fdb5d9b0d26b9f56d057ef/docs/IMPLEMENTATION_STATUS.md) preserves foundation/auth/lifecycle/classroom slices. E08-04 d437edf browser UI committed; CI/manual acceptance pending. E08-02/03 7e3792c no supplied CI result. E08-01 6929d69 CI_PASSED by owner November 15 15:50 report, run https://github.com/pavanjains/lms/actions/runs/43758274124 ; fetch failed, not independently verified, no count supplied. No local migration/manual success inferred.

BUG-001/002 verified by earlier owner reports; historical BUG-002 log 83 entries/one import error/82 passed, no onboarding methods executed; later e3bcfcb pass reported without count. BUG-003 local fix reported working, full browser checks pending; E05-07 manual session-deactivation acceptance pending. New tests not covered by previous passes.

## Limits / next
Controlled two-transaction service interleavings, not proof of every schedule, all user/org mutation paths, raw ORM safety, load, session revocation or E05 invitation races. MFA proof stubbed, HTTP/browser not exercised. Locks serialize cooperating organization services. Shared-instructor browser checks in CLASSROOMS_UI.md remain open.

Student creation/initial access and sessions, lessons/documents/assignments, progress/feedback/reports, privacy/retention/shared-device isolation, recovery/throttling/session/last-owner controls, audit/log redaction, approved mail, dependency/Python 3.14 CI, deployment/restore/monitoring/training remain incomplete. Staff flags remain disabled by default. Passing CI alone is not production approval.
