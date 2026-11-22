# Robotics LMS — Action Plan

Updated 2026-11-22. Baseline main 88524ab8788fc61b72c2a4d8ff19ccbdee38d159; feature/class-roster-assignments. No production approval.

ROSTER-ASSIGN-01 is IN_PROGRESS: roster selection reuses signed assignment review/confirmation and transactional services; success returns to class; class history is independently paginated. 15 regression methods are authored, not executed by the author. No migration.

Next: exact-head CI lint/system/migration checks and full PostgreSQL suite; keyboard/no-JavaScript/select-page/preview/error/cancel/back/reload browser cases; PR review and expectedHeadSha merge guard. See docs/ASSIGNMENTS.md. Skip-link defect remains separate.

ASSIGN-01 and ASSIGN-02 remain IN_PROGRESS. PR #4 is merged at f3cc9e2 per HANDOFF.md. CI on 88524ab, assignment after final Confirm, progress persistence and status-only privacy are owner-reported only. Migration 0003 deployment and Python 3.14 remain unverified. Stale-update, A/B, identity-switch, reset/expiry/revocation, durable token concurrency, progress history/reporting and TextField service validation remain open. Existing security/operations/document/branding gates, E08-05 and BUG-003 remain open; PDFs stay restricted. Update tracking and attributed validation with every implementation commit.

Earlier failures/evidence are retained in docs/VALIDATION.json and the historical plan:
https://github.com/pavanjains/lms/blob/88524ab8788fc61b72c2a4d8ff19ccbdee38d159/ACTION_PLAN.md

## Roster test correction, 2026-11-22
Owner-supplied CI log: 353 tests in 13.113s, one failure, clean system check, exit 1; run ID/revision/runtime not supplied. The anonymous client incorrectly expected 405 before StaffAuthMiddleware's login redirect. Test now checks anonymous and password-only redirects, then MFA-verified 405; application guards unchanged. Replacement-method syntax checked; retest pending. Do not create the previously proposed PR without fresh approval.
