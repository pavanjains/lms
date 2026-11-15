# Implementation Status

Updated: 2026-11-15, 13:43 EST.

[Action plan](../ACTION_PLAN.md) records roadmap/release gates; [ticket ledger](TICKETS.md) records evidence and supersedes historical feature notes.

## Previously committed
- Foundation, PostgreSQL configuration and organization/user/profile migrations.
- Configuration/CI (1311cd3); bootstrap (ce49752), corrected by ef6b96c, BUG-001.
- Staff email/password backend and MFA guard (b3aca8d).
- Gated MFA enrollment/login, recovery codes, POST logout and workspace (031b843).
- Invitation schema/lifecycle services (d60ab7d).
- Owner lists, search, pagination, statuses and revoke UI (0ce5595).
- Gated invite/email/resend/activation and fourteen tests (1b4a5dd).
- Test mail-import correction (e3bcfcb, BUG-002); passing workflow owner-confirmed at 13:28 EST. cd1f580 records that confirmation.

## Current E05-07 increment
Owner-only, organization-scoped instructor deactivation with GET review, confirmed CSRF-protected POST, transactional owner revalidation, retained account/password/MFA/related records and targeted removal of unexpired database sessions. No owner/student/foreign-organization target can be deactivated. Repeated requests are safe. Unsupported session engines are rejected; reactivation not implemented. Existing backend/policies reject inactive staff on subsequent requests, including a concurrent sign-in that writes another session.

Fourteen tests authored for confirmation, retained records, multiple sessions, login/access denial, owner-session preservation, permissions, role/organization boundaries, CSRF, feature gate, stale actor validation, backend rejection and rollback. Runtime tests and browser acceptance NOT RUN here. CI PENDING. New listing control is part of this unverified increment, not retroactively covered by earlier passing CI.

## Evidence boundaries
Latest reported passing application commit remains e3bcfcb, based on owner's 13:28 EST confirmation. BUG-002 stays FIXED_VERIFIED. Passing run URL/count/logs unavailable; Actions not independently retrieved and no new passing count inferred. cd1f580 has no separately supplied workflow result.

Historical 13:21 EST failure: 83 test entries in 0.897s, one onboarding module-import error, other 82 entries passed; onboarding methods did not execute. Preserve this separately from the later passing report.

## Operational limits
No migration, real account action, email, credential change or feature-flag activation by the source commit. Staff authentication and onboarding remain off by default. No production or manual-browser acceptance claimed. Reactivation, audit, PostgreSQL race testing, throttling, approved session limits, recovery, activation-path log redaction and approved mail/delivery policies remain open. In-flight requests are not retroactively cancelled.

Classes, student access, lessons, documents, assignments, progress, feedback, reports, deployment and broader release gates remain incomplete. Passing CI alone is not production authorization.
