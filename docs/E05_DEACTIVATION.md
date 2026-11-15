# E05-07 instructor deactivation

Status REVIEW; CI and manual browser acceptance PENDING. Fourteen tests authored, not executed in the authoring environment. No migration or feature-flag change. This source commit does not deactivate any runtime account.

## Behavior
Verified active owners can review an instructor in their own organization and confirm a CSRF-protected POST. GET never deactivates. The transaction rechecks the owner in the database, locks the organization then target user, marks only INSTRUCTOR accounts inactive and removes that user's unexpired authenticated database sessions. Owner/student/foreign-organization IDs cannot be targeted. Repeating a confirmed request is safe and repeats session cleanup.

The account, password hash, MFA devices and related records remain. No delete, reactivation, reassignment, audit schema or notification is introduced. Session cleanup and deactivation roll back together on failure. Staff backend and per-request policies independently reject inactive staff. Existing protected requests already in flight are not retroactively cancelled; a sign-in racing with deactivation may write another unusable session, but inactive users remain denied on subsequent requests.

## Session-backend boundary
Current base settings use django.contrib.sessions.backends.db. This implementation explicitly rejects other engines, including cached_db and signed cookies, rather than claiming to revoke sessions it cannot remove. It scans unexpired database session payloads to identify the target; only matching session keys are deleted. This is bounded by deployed session volume, not account count; revisit indexing/session registries before larger deployment. No decoded session contents or credentials are logged by this service. Expired rows remain for normal clearsessions maintenance.

## Manual acceptance
1. With synthetic data and staff auth explicitly enabled locally, sign in as owner with MFA and open instructor management.
2. Review an active instructor; verify identity, cancel, and confirm no state change.
3. Open two verified instructor browser sessions and an unrelated owner session.
4. Confirm deactivation as owner. Verify inactive status, retained account/MFA, both instructor sessions denied on next protected request, and owner access retained.
5. Verify fresh instructor login fails, repeat submission is safe, cross-organization/owner/student IDs are blocked, and CSRF protection is enforced.
6. Record environment, revision and observed results separately from CI. Do not enable production access based on unit tests alone.

Reactivation needs a separate reviewed workflow. Durable audit, PostgreSQL race tests, recovery, throttling, session limits and other release gates remain open.
