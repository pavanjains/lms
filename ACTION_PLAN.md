# Robotics LMS — Action Plan

Updated: 2026-11-15, 15:19 EST. Repository: pavanjains/lms; main.

## Current increment
E08-01: apps/classrooms model foundation, AppConfig registration, initial migration and model tests authored. Status REVIEW; CI, migration execution and drift checks PENDING. No runtime database changes performed here. No routes/UI, permission services, student login, account creation or feature-flag activation. Cross-record validation requires explicit full_clean(); raw ORM writes can bypass it. See docs/CLASSROOMS.md.

E08-02 transactional services and E08-03 scoped policies are next. E08-04 UI and E08-05 PostgreSQL concurrency/browser acceptance follow. Sharing a student must not grant access to unrelated class records.

## Prior state and evidence
[Preserved action plan at 24453d6](https://github.com/pavanjains/lms/blob/24453d623785f1ff560c3444bcb5eedbb564a36c/ACTION_PLAN.md) retains the preceding roadmap/history. docs/TICKETS.md is authoritative; implementation/fix commits update this file, that ledger and docs/IMPLEMENTATION_STATUS.md. Markdown IDs are not GitHub Issues; no unattended tracking automation.

BUG-003 committed at 24453d6: same-origin onboarding header, updated assertion and five CSRF regression methods; fourteen original onboarding methods retained. Owner reported the local one-line fix worked at 15:07 EST. Full CI, activation/resend browser acceptance PENDING. E05-07 at 666eee6 remains REVIEW: fourteen authored tests, CI/browser acceptance PENDING.

Latest reported passing application commit remains e3bcfcb (owner 13:28 EST); URL/count unknown, Actions not independently retrieved. BUG-002 remains FIXED_VERIFIED on that evidence. Historical 1b4a5dd mail-import failure: owner 13:21 log, 83 entries, one import error, 82 passing entries; no onboarding methods executed. cd1f580 recorded the passing report; no separate result supplied. No new passing counts inferred.

## Roadmap
- E01–E03: Partial; dependency lockfile/setup/shared UI open.
- E04: Partial; password/MFA recovery, throttling, last-owner and session controls open.
- E05: Implemented lifecycle portions; new CI/manual verification, audit/delivery/concurrency remain.
- E06–E08: Baseline students plus E08-01 authored schema; services, policies and student access remain.
- E09–E17: Documents, lessons, assignments, progress, feedback, workspaces and reports TODO.
- E18–E22: Audit, deployment/recovery, full acceptance, training and launch incomplete.

## Next actions and release gates
1. Run E08-01 checks, migration drift check and full PostgreSQL tests; preserve actual evidence.
2. Implement E08-02/03 with active actor/MFA checks, organization/class isolation and negative tests before exposing UI.
3. Complete BUG-003 and E05-07 CI/browser verification and E05 race/delivery follow-ups.
4. Review Python 3.14 dependencies and CI; local metadata edits are not committed support.
5. Resolve recovery, throttling, session limits, token-path log redaction, approved mail origin/sender, audit and delivery policy before operational access.
6. Complete shared-device isolation, content/workflows/reports, privacy/retention, backups/restore, monitoring, browser UAT and training before launch.

Staff auth and onboarding remain off by default. No production approval; passing CI alone does not authorize deployment.
