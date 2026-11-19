# Robotics LMS — Action Plan

Updated: 2026-11-18, 21:05 EST. Repository pavanjains/lms; main.

## E08-08 authored
Separate gated student backend and /students/login/, /students/, POST logout. Self-only profile/class-name dashboard; no requested student IDs, lessons/submissions/completion controls. One identity per browser profile; explicit logout before switching, staff sessions not replaced, student staff-route attempts denied without silently logging them out. Anonymous context flushed, session key/CSRF rotated by Django login. Current active student/profile/org and nonstaff flags rechecked; database sessions only.

Provisional idle 900s/absolute 14400s; malformed/missing timestamps fail closed. Student backend locks organization/user; login saves session inside outer transaction to share reset lock ordering. Password-hash/session revocation, expiry, role/account/org changes covered by authored unit/client tests, NOT RUN here. PostgreSQL simultaneous reset/login and browser/BFCache checks still required. LMS_STUDENT_AUTH_ENABLED remains false by default; no production enablement. See docs/STUDENT_SIGN_IN.md.

## Evidence update
Owner stated CI for all have passed November 18 21:02 EST, covering committed work through 460d7fa. Record as user-reported, not independently retrieved; no counts/new run URLs supplied. E08-02/03/04/06/07 CI_PASSED on that report; E08-05 concurrency portion CI passed but overall IN_PROGRESS for manual/race-extension work. Prior E08-01 report/run and BUG history preserved in linked ledger. This report does not cover E08-08 or close browser/production gates.

[Previous full plan](https://github.com/pavanjains/lms/blob/460d7fabe91df823f81766bd5d84756102679f3a/ACTION_PLAN.md) retains history. No migration/runtime account/password action or flag activation in this source increment.

## Next
1. Run new/full CI and synthetic student A/B, staff MFA and shared-device/browser acceptance.
2. Extend PostgreSQL tests for creation/reset/login/access-removal races and session-save interleavings; include cookie replay and back navigation.
3. Approve practical child credential/session UX; implement throttling/audit before real-user access.
4. Lessons/documents/assignments, instructor progress/feedback and read-only student learning workspace.
5. Recovery/last-owner/staff session controls, TLS/log redaction/privacy/mail, dependency/Python 3.14 CI, deployment/restore/training remain open.

Update this plan, docs/TICKETS.md and docs/IMPLEMENTATION_STATUS.md per implementation/fix. Existing staff/onboarding flags unchanged; no unattended tracking or launch approval.

## BUG-004 update — 2026-11-18, 21:14 EST
Owner reports E08-08 CI lint failure after a372751: Ruff F401 at apps/accounts/test_students.py:10:53, unused ClassInstructor import; one lint error. Correction removes only that imported name. All student test bodies/assertions retained; runtime behavior, migrations and flags unchanged. Fix authored, not executed here; rerun CI PENDING. No test execution outcome/count inferred from the lint log. Earlier owner-reported passes through 460d7fa remain unchanged.
