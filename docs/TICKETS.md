# Development Tickets and Fix Ledger

Updated 2026-11-22 on fix/skip-to-content, source baseline main 6e3dd234417f831acd3a5362cad3adb0e4fb6d84. IDs are local ledger labels, not GitHub issue numbers. No production approval.

## Skip-to-content defect — IN_PROGRESS; fix authored, acceptance pending
Owner reported nonfunctional link on all pages. Retrieved base template has matching #main/main ID but lacks tabindex/focus indicator. Add tabindex=-1 and visible focus outlines in the shared layout, retaining first visible native link/no-JavaScript behavior and no autofocus/positive tabindex. This is a source-level focusability correction, not an independently reproduced browser diagnosis. Six new structural regression methods cover public/staff/student/error pages, matching unique target and focus styles. Python syntax/compile and authored HTML structure checked; Django/Ruff/rendering/CI/browser NOT RUN by author. Procedures/limits: SKIP_LINK.md. Not FIXED_VERIFIED. No route/auth/session/CSRF/credential/flag/database change.

## BUG-003 — REVIEW; verification increment merged
Instructor-onboarding null-origin/CSRF defect is separate from skip link and migration 0003. Historical 24453d6 no-referrer to same-origin correction/local confirmation and included CI pass were owner-reported. PR #6 merged at 7a82d695528d1b0db4ea20dda2ca04b82173464d, guarded head d2784b9; 10 HTTPS/CSRF methods and guide updates, no runtime security change. Successful head checks independently retrieved: 45082944989/check137394965797 and 45083255954/check137395959713. No passing count. Browser and actual token-path logging acceptance remain open; no production redaction or closure claim. Historical scope: https://github.com/pavanjains/lms/blob/ded6acb393cb80f20bd3394e6f7c3724ccb40ec7/docs/TICKETS.md

## ROSTER-ASSIGN-01 — IN_PROGRESS; source merged
PR #5 merged at a0cd91b78f7d38c885e64f526ade8285b2b82e53, guarded head 83c86a3; roster selection/count/select-page/no-JavaScript, preselection/previews, signed review/final confirmation/cancel/class return and scoped paginated history, 15 new methods. Existing services/central history retained, no feedback in roster/automatic enrollment assignment/new migration/exactly-once guarantee. Successful head checks independently retrieved: 45081121549/check137389292906 and 45081792433/check137391367330. PR #5 merge-specific run unverified. Browser A/B/keyboard/error/pagination/back/reload acceptance open.

## CI reports and failure history retained
Owner-reported only: latest main after PR6 at 18:30 EST and docs 6e3dd23 at 18:38 EST, associated by conversation; run IDs/tested SHAs/runtime/counts not supplied or independently retrieved. These reports do not cover this feature commit. No passing totals inferred.

- Roster initial run: supplied log 353 tests, one failure in 13.113s, clean system check/exit1, run/revision unknown. Anonymous self.client wrongly expected 405 before staff login redirect. Corrected 83c86a3 checks anonymous/password-only redirect then verified-MFA405, retaining CSRF checks; later pre-merge checks successful. Failure retained, 353 not a passing total.
- BUG-006 UUID serialization: f52a592 run44667767312, supplied log296 tests/9 errors; fixed ddc000b, checks44668593439/44668981076 independently successful.
- Feedback length: c9b76e2 supplied log338 tests/2 failures from one test, no runID; fixed23a9d2d, checks44846492681/44846822307 independently successful.
- Student UI ebdb9ea checks44834522871/44834596308 and earlier PR4 f5ec991 checks44847456934/44847462963 remain previously retrieved evidence, not re-retrieved now. Earlier BUG001/002/E05/E08 and other main CI history remains linked and in VALIDATION.json.

ASSIGN-01/02 remain IN_PROGRESS; PR4 progress/feedback merged at f3cc9e2. Student status only, never feedback/write controls. Prior assignment after Confirm/progress persistence/privacy checks owner-reported, not full acceptance. Migration0003 application, progress history/reporting, durable review concurrency, service TextField validation and Python3.14 unverified. E08-05 remains IN_PROGRESS; E08-08/BUG004/BUG005 retain prior owner-report attribution. Branding/library/document/file safety/student delivery/shared-device/races/audit/throttling/recovery/session/TLS/privacy/retention/mail/deployment/backup/training gates remain.

Prior detailed snapshot/history: https://github.com/pavanjains/lms/blob/6e3dd234417f831acd3a5362cad3adb0e4fb6d84/docs/TICKETS.md
