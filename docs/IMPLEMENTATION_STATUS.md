# Implementation Status

Updated: 2026-11-15, 15:09 EST.

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

## Current BUG-003 increment
Shared onboarding response Referrer-Policy changed from no-referrer to same-origin to fix browser POST rejection with Origin null. Existing header assertion updated; five CSRF-enforced regression methods authored for same-origin invite/resend/activation and null/cross-origin invite/activation rejection. Fourteen original onboarding methods retained. Tests authored, NOT RUN here; new CI PENDING. Django test clients do not generate browser Origin behavior, so full browser acceptance is separate.

Owner confirmed the one-line local fix worked at 15:07 EST. This is user-reported invitation-flow evidence only, not full activation/deactivation acceptance or independent CI verification. Cross-origin referrers remain suppressed by the policy; same-origin token paths can still reach internal logs, so log redaction remains open. No CSRF exemption or null-origin allowlisting.

## E05-07 increment at 666eee6
Owner-only, organization-scoped instructor deactivation with GET review, confirmed CSRF-protected POST, transactional owner revalidation, retained account/password/MFA/related records and targeted removal of unexpired database sessions. No owner/student/foreign-organization target can be deactivated. Repeated requests are safe. Unsupported session engines are rejected; reactivation not implemented. Existing backend/policies reject inactive staff on subsequent requests, including a concurrent sign-in that writes another session.

Fourteen tests authored for confirmation, retained records, multiple sessions, login/access denial, owner-session preservation, permissions, role/organization boundaries, CSRF, feature gate, stale actor validation, backend rejection and rollback. Runtime tests and browser acceptance NOT RUN here. CI PENDING. New listing control is part of this unverified increment, not retroactively covered by earlier passing CI.

## Next implementation scope
E08-01/02/03 are scoped in the ledger and remain TODO: class/membership/enrollment schema, transactional validated services, organization/class-scoped policies and tests. Class UI and student sign-in are not included in BUG-003. No background implementation is running. Python 3.14 support also remains unverified; local metadata edits are not committed by this fix.

## Evidence boundaries
Latest reported passing application commit remains e3bcfcb, based on owner's 13:28 EST confirmation. BUG-002 stays FIXED_VERIFIED. Passing run URL/count/logs unavailable; Actions not independently retrieved and no new passing count inferred. cd1f580 has no separately supplied workflow result.

Historical 13:21 EST failure: 83 test entries in 0.897s, one onboarding module-import error, other 82 entries passed; onboarding methods did not execute. Preserve this separately from the later passing report.

## Operational limits
No migration, real account action, email, credential change or feature-flag activation by the source fix. Staff authentication and onboarding remain off by default in repository settings; owner explicitly enabled local flags for testing. No production acceptance claimed. Reactivation, audit, PostgreSQL race testing, throttling, approved session limits, recovery, activation-path log redaction and approved mail/delivery policies remain open. In-flight requests are not retroactively cancelled.

Classes, student access, lessons, documents, assignments, progress, feedback, reports, deployment and broader release gates remain incomplete. Passing CI alone is not production authorization.
