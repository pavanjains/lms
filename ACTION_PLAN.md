# Robotics LMS — Action Plan

Updated: 2026-11-18, 19:58 EST. Repository pavanjains/lms; main.

## Current E08-04 increment
Classroom browser UI authored: list/detail, owner create/archive, owner instructor assignment/removal, scoped enrollment/end-enrollment, confirmation forms, staff navigation and UI tests. Status REVIEW, CI/browser acceptance PENDING. No runtime database change, seed accounts, email, migration or flag activation. Services reauthorize every write; lists/selectors scoped, no full User records in roster context. See docs/CLASSROOMS_UI.md.

## Evidence
E08-01 6929d69 CI_PASSED by owner's November 15 15:50 EST report: https://github.com/pavanjains/lms/actions/runs/43758274124 . Fetch failed; not independently verified, no count supplied. Local migration/manual acceptance not implied. E08-02/03 7e3792c committed November 18; no CI result supplied. E08-04 tests authored, not executed here.

BUG-003 24453d6 local invitation fix owner-confirmed November 15 15:07; full browser acceptance open. E05-07 666eee6 manual deactivation/session acceptance remains open. BUG-001/002 and earlier reported pass evidence retained in ledger history. No inferred counts.

## Next
1. Run E08-04 and full PostgreSQL CI; synthetic owner/instructor browser acceptance.
2. E08-05 PostgreSQL race tests and end-to-end shared-instructor isolation.
3. Instructor-managed student creation with initial access, student sessions/shared-device isolation. No student creation form is included here; enrollment uses existing accounts.
4. Lessons/supporting documents, assignments, instructor progress/feedback, student read-only workspace and reporting.
5. Recovery/throttling/session/last-owner controls, audit, log redaction, mail approval/delivery, Python 3.14 CI, reproducible dependencies and deployment/restore/privacy/training remain release gates.

[Prior complete plan](https://github.com/pavanjains/lms/blob/7e3792c115769739fc1a200db1bc366123a700b2/ACTION_PLAN.md) preserves prior roadmap/evidence. Update ACTION_PLAN.md, docs/TICKETS.md and docs/IMPLEMENTATION_STATUS.md in each implementation/fix. Flags remain off by default, no production authorization or unattended tracking.
