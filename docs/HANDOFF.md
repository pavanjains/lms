# Handoff: Robotics LMS (pavanjains/lms)

Updated Sunday 2026-11-22 after the 18:30 EST owner CI report. Point-in-time source baseline main 7a82d695528d1b0db4ea20dda2ca04b82173464d, before this documentation-only commit. TICKETS.md and VALIDATION.json hold current attributed evidence. Nothing is production-approved.

## Resume point
- PR #5 merged class-roster assignments at a0cd91b78f7d38c885e64f526ade8285b2b82e53, head 83c86a3776a509350c02df74b4b3dbbb7d026e35; expectedHeadSha matched. Implementation commit 976e755, test correction 83c86a3. Fifteen new regression methods.
- PR #6 merged BUG-003 HTTPS onboarding verification at 7a82d695528d1b0db4ea20dda2ca04b82173464d, head d2784b90c3826c9a8502aa6ea432167b017768c1; expectedHeadSha matched. Ten new regression methods; tests/docs only, existing same-origin/CSRF runtime behavior retained.
- ASSIGN-01, ASSIGN-02 and ROSTER-ASSIGN-01 remain IN_PROGRESS. BUG-003 remains REVIEW pending browser and token-path logging acceptance; it is not the skip-link defect or migration 0003.
- PRs #1/#2/#3/#4 earlier merged at 9012dd1/92ed0ab/4695e7d/f3cc9e2.

## CI evidence and limits
| Scope | Evidence | Attribution |
|---|---|---|
| PR #5 head 83c86a3 | runs 45081121549, 45081792433 successful | Independently retrieved pre-merge; no passing count |
| PR #6 head d2784b9 | runs 45082944989, 45083255954 successful | Independently retrieved pre-merge; no passing count |
| Latest main after PR #6 merge | owner says CI passed at 18:30 EST | Owner-reported only; run ID/tested SHA/runtime/count not supplied |
| PR #5 merge-specific CI | Not verified | Do not infer from later-head checks or latest owner report |

The latest report is associated with main after PR #6 by conversation context, not a supplied run/SHA. It does not cover this later docs commit. Earlier successful head checks and failures remain in VALIDATION.json/TICKETS.md. The author did Python syntax/compile checks, not Django/Ruff/template/browser/PostgreSQL execution. No passing total is inferred from authored methods or successful jobs.

Retain three reported failures: UUID serialization, 296 tests/9 errors (44667767312); feedback length, 338 tests/2 failures from one test (no run ID); roster authentication-order expectation, 353 tests/one failure in 13.113s (run/revision unknown). Later passes do not erase them. Earlier handoff also records PR #4 f5ec991 checks 44847456934/44847462963 and 23a9d2d checks 44846492681/44846822307, and PR #3 ebdb9ea checks 44834522871/44834596308 as independently retrieved at the time.

## Current behavior
Class roster supports visible-page student selection, select-page/count/no-JavaScript fallback, preselected assignment form, lesson previews, exact signed review/explicit Confirm, POST review cancellation and signed return to class. Class history has separate pagination and existing detail/progress links; central history remains. No automatic assignments for later enrollments, partial-batch creation or durable exactly-once review-token guarantee.

Staff progress statuses: Assigned, In progress, Reviewed, Needs revision; latest optional feedback up to 2000 characters. Students see status only, never feedback or progress controls. No progress history/reporting. BUG-003 adds HTTPS Origin/Referer regressions without weakening CSRF. Guide: E05_ONBOARDING.md; simulated secure test requests do not establish browser/TLS/proxy/logging acceptance.

## Owner-reported local and browser context
- Local .venv314 with Python 3.14.2; project requirement >=3.12,<3.15. Compatibility remains unverified.
- Local PostgreSQL previously inspected as 127.0.0.1:5432, database robotics_lms. Existing active organization Local Robotics Center and owner localowner (owner@example.test). These are prior reports, not a fresh database inspection.
- Do not rerun bootstrap: it already refused because organization data exists. Preserve data/local changes. Instructor password recovery was directed to interactive changepassword; password/MFA outcome not reported. Never put passwords, OTP secrets, invitation/review tokens or cookies in evidence.
- Owner reported assignment worked after final Confirm, staff progress persisted after reload and student status-only/no-feedback/no-controls privacy check completed. Not independently verified and not full acceptance.

## Next work and release boundaries
1. Diagnose the owner-reported Skip to content failure on all pages. Cause undiagnosed; no skip-link fix has been implemented.
2. Browser-check roster selection/count/keyboard/select-page/no-JavaScript, previews/errors/Confirm/cancel/back/reload, history and student A/B isolation. Continue stale-update, identity-switch/back/reload, reset/expiry/revocation and broader browser acceptance.
3. Complete BUG-003 onboarding browser checklist and actual token-path logging inventory/redaction verification across application/server/proxy/CDN/APM/mail/retained sinks. No production redaction implementation/verification; keep REVIEW.
4. Verify existing migration 0003_assignment_progress application on the intended database. It is already on main. No deployment/application evidence supplied; old wording applied nowhere is not a current inspection. Review status/plan and back up before any deliberate database write. Do not infer migration application from browser/CI/source.
5. Progress history/reporting; durable review-token concurrency; possible service TextField length validation for lesson/assignment summary/instructions. Keep security/operations/document/branding, E08-05, throttling/audit/recovery/session/TLS/privacy/retention/mail/file safety/deployment/backup/restore/training gates open. PDFs remain restricted; no approved student document delivery.

Current tracking/evidence supersedes dated authoring-time pending-CI notes in feature guides. Guides remain procedures, not execution reports. No runtime changes, deployment, database migration, feature activation or production authorization are performed by this docs update.

## Workflow and cleanup
Confirm every external write with exact payload. Implementation uses feature branch/PR; guard merges with expectedHeadSha after current checks/review. Main docs-only writes are allowed when explicitly requested. Every implementation/fix updates action/tickets/status/affected guides/validation, retaining attribution and earlier failures.

Remote feature/class-roster-assignments and fix/bug-003-onboarding-verification were still present after their merges. They have not been deleted; deletion is a separate confirmed action after checking refs. Preserve local changes before fetch/pull/switch/prune. No access to the user's local clone/browser is implied.

Code: apps/lessons assignment services/views/student queries and templates; apps/accounts/onboarding.py with test_onboarding.py and new test_onboarding_csrf_https.py. Reuse fresh actor/object/class authorization and version-checked service patterns. Test fixture helpers are borrowed explicitly. GitHub push_files takes whole files; authoring state does not persist across messages.

Previous handoff: https://github.com/pavanjains/lms/blob/7a82d695528d1b0db4ea20dda2ca04b82173464d/docs/HANDOFF.md
