# Robotics LMS — Action Plan

Updated: 2026-11-15, 15:50 EST. Repository: pavanjains/lms; main.

## Current increment
E08-02/E08-03 services and scoped policies authored; status REVIEW, new CI PENDING. Owners create/archive classes and manage instructor links. Assigned instructors manage their class enrollments; adding students requires existing student visibility. Organization lock, fresh actor/role/active checks, MFA and staff flag required. Memberships are retained and repeat-safe. No routes/UI, migrations, account creation or flag activation. Tests authored, not executed here. See docs/CLASSROOMS_ACCESS.md.

## Verification
Owner reports E08-01 6929d69 workflow succeeded at 15:50 EST: https://github.com/pavanjains/lms/actions/runs/43758274124 . Recorded CI_PASSED on that report; URL fetch failed, Actions not independently verified. No test count/logs supplied. Local migration execution and browser acceptance are not implied. Earlier commits are not independently reclassified.

BUG-003 24453d6 local one-line fix reported working 15:07 EST; E05-07 666eee6 manual acceptance remains pending. Earlier passing e3bcfcb report and BUG-001/002 histories retained in docs/TICKETS.md and its immutable baseline links. No new passing counts inferred.

## Roadmap / next
1. Run new E08 service/policy and full PostgreSQL CI; record actual results.
2. E08-04: MFA/CSRF-protected class list/create/detail, staff membership and scoped enrollment UI.
3. E08-05: PostgreSQL races and shared-instructor browser acceptance; review user role/organization changes against class links.
4. Student creation/access, lesson/document library, assignments, progress/feedback and reports remain ahead. Student creation must establish initial access; no instructor-wide student directory.
5. Recovery, throttling, last-owner/session controls, audit, token-path log redaction, approved mail/delivery and Python 3.14 CI remain open.
6. Shared-device/privacy/retention, backup restore, monitoring and operational UAT/training remain release gates.

[Prior plan](https://github.com/pavanjains/lms/blob/6929d69be5d009831588712694b43a3238006e32/ACTION_PLAN.md) preserves preceding roadmap/evidence. E01–E04 foundations/auth remain partial; E05 lifecycle hardening remains; E06–E08 classroom/student work partial; E09–E22 content/workflow/operations incomplete. Every implementation/fix updates this file, docs/TICKETS.md and docs/IMPLEMENTATION_STATUS.md. Staff flags remain off by default. No production approval or unattended work implied.
