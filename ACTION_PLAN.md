# Robotics LMS — Action Plan

Updated: 2026-11-18, 20:17 EST. Repository pavanjains/lms; main.

## Current E08-06
Instructor-managed student creation authored: authorized active-class form, validated password hashing, atomic User/StudentProfile/enrollment, fixed STUDENT role and organization, no staff privileges/email requirement. Owner may use any active same-organization class; instructor needs active membership. Initial access is enrollment-based for all assigned instructors, not permanent creator ownership. No new migration, student sign-in, credential handout/reset or flag activation. Status REVIEW; tests NOT RUN here, new CI/browser acceptance PENDING. See docs/STUDENT_CREATION.md.

## Existing evidence
E08-01 6929d69 CI_PASSED only by owner's November 15 15:50 report, run https://github.com/pavanjains/lms/actions/runs/43758274124 ; fetch failed, not independently verified, count unknown. E08-02/03 7e3792c, E08-04 d437edf and E08-05 concurrency 7f97933 committed; no CI results supplied. E08-05 remains IN_PROGRESS with browser acceptance open. No inferred test counts.

[Previous complete plan](https://github.com/pavanjains/lms/blob/7f97933d1666b443f5d12aba01f98ac9427939c4/ACTION_PLAN.md) preserves roadmap/history. BUG-001/002 prior owner verification preserved; BUG-003 local fix owner-confirmed, full browser acceptance open; E05-07 manual session acceptance open.

## Next / release gates
1. Run student creation, classrooms and full PostgreSQL CI; verify synthetic browser creation/shared access and rollback/duplicate handling.
2. Extend PostgreSQL concurrency coverage to student creation conflicts and membership/archive changes; E08-05 existing cases do not cover this new service.
3. Complete owner/shared-instructor browser acceptance.
4. Student sign-in/credential delivery/reset/shared-device isolation; no student submissions or completion controls.
5. Lessons/documents/assignments, instructor progress/feedback and student read-only workspace/reporting.
6. Recovery/throttling/session/last-owner/audit/log-redaction/mail approval, dependency/Python 3.14 CI and deployment/restore/privacy/training remain open.

All implementation/fix commits update this plan, docs/TICKETS.md and docs/IMPLEMENTATION_STATUS.md. Staff flags remain off by default; no runtime accounts created by source commit, no launch authorization/unattended work.
