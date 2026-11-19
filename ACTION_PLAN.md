# Robotics LMS — Action Plan

Updated: 2026-11-18, 20:09 EST. Repository pavanjains/lms; main.

## Current E08-05 concurrency increment
PostgreSQL TransactionTestCase tests authored with separate worker connections, uncommitted leader transactions, observed pg_blocking_pids waits and bounded release/SQL/future timeouts. Cases cover duplicate class names, assignment/enrollment reuse, removal/archive/deactivation versus enrollment in both orders, and end/re-enroll ordering. Runtime services unchanged. CI now asserts PostgreSQL and has a job timeout; full suite discovers the tests. SQLite skips are not concurrency evidence.

Status E08-05 IN_PROGRESS: concurrency code REVIEW, tests NOT RUN here, CI PENDING; shared-instructor/browser acceptance still open. No migration, runtime account/database action, mail, flag activation or production approval. See docs/CLASSROOMS_CONCURRENCY.md.

## Evidence retained
E08-01 6929d69 CI_PASSED by owner's November 15 15:50 report: https://github.com/pavanjains/lms/actions/runs/43758274124 . Fetch failed, not independently verified, no count supplied. Local migration/manual checks not implied. E08-02/03 7e3792c and E08-04 d437edf committed; no CI results supplied. New concurrency tests not covered by prior reports.

[Previous complete plan](https://github.com/pavanjains/lms/blob/d437edf410412d40e9fdb5d9b0d26b9f56d057ef/ACTION_PLAN.md) preserves roadmap and history. BUG-003 local fix owner-confirmed, full browser acceptance open; E05-07 manual session/deactivation acceptance open. BUG-001/002 historical evidence preserved in ledger links; no inferred passing counts.

## Next / release gates
1. Run PostgreSQL concurrency and full CI; investigate errors/timeouts rather than silently skip.
2. Complete E08-04/E08-05 owner/shared-instructor browser acceptance; include access loss after membership/account changes.
3. Instructor-managed student creation/initial access and shared-device sessions.
4. Lessons/documents, assignments, instructor progress/feedback and student read-only workspace/reporting.
5. Recovery/throttling/session/last-owner controls, audit, log redaction, approved mail/delivery, dependency locking/Python 3.14 CI and deployment/restore/privacy/training remain open.

Update this file, docs/TICKETS.md and docs/IMPLEMENTATION_STATUS.md in each implementation/fix commit. Staff flags remain off by default; no unattended tracking or launch authorization.
