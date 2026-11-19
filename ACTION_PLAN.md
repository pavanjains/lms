# Robotics LMS — Action Plan

Updated: 2026-11-18, 20:23 EST. Repository pavanjains/lms; main.

## Current E08-07
Scoped student password reset and credential receipt authored. Owner or assigned instructor reviews an active enrolled student, confirms CSRF-protected POST, receives generated password in that response only. New validated password hash and unexpired database-session revocation share a transaction. Staff/other accounts untouched. No existing-password retrieval, plaintext session/message/URL storage, email or automated handout. Database session engine only; unsupported engines fail closed. Tests authored, NOT RUN here; status REVIEW, new CI/browser acceptance PENDING. See docs/STUDENT_CREDENTIALS.md.

## Evidence
E08-06 873cbb4 student creation committed; no CI result supplied. E08-05 7f97933 concurrency and E08-04 d437edf UI committed; no supplied results. E08-02/03 7e3792c remain REVIEW. Only recent reported pass is E08-01 6929d69, owner November 15 15:50 report with https://github.com/pavanjains/lms/actions/runs/43758274124 ; fetch failed, not independently verified/count unknown. No manual success or new counts inferred.

[Previous full plan](https://github.com/pavanjains/lms/blob/873cbb4ebb9c028c0985c6d2135c46572c2241e7/ACTION_PLAN.md) preserves roadmap/history. BUG-001/002 prior owner evidence retained; BUG-003 local fix reported working/full browser pending; E05-07 manual session acceptance pending.

## Next / gates
1. Run reset/creation/classrooms/full PostgreSQL CI and synthetic browser tests.
2. Extend races to student creation/reset and simultaneous credential issuance, access revocation and login. Existing E08-05 cases do not verify these new paths.
3. Complete shared-instructor browser acceptance.
4. Student sign-in/shared-device isolation and reviewed credential-delivery/reset UX. Generated password is not auto-expiring/single-use.
5. Lessons/documents/assignments, instructor progress/feedback and student read-only workspace/reporting.
6. Audit, reset/login throttling, recovery/session/last-owner controls, TLS/log redaction/privacy/mail approval, dependency/Python 3.14 CI and deployment/restore/training remain release gates.

No schema/migration, feature-flag activation or runtime credential action by source commit. Staff flags remain off by default. All implementation/fix commits update this file, docs/TICKETS.md and docs/IMPLEMENTATION_STATUS.md. No production approval/unattended work.
