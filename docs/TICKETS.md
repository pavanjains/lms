# Development Tickets and Fix Ledger

Updated 2026-11-22; branch fix/lesson-text-validation, baseline main ff2f68c. Ledger labels are not GitHub issue numbers. No production approval.

## Lesson text validation — IN_PROGRESS; hardening authored, CI pending
Add shared MaxLengthValidator helper using existing Lesson/LessonAssignment summary2000 and instructions20000 model limits. Call after normal cleaning before create/edit saves and source/snapshot assignment writes. Preserve whitespace semantics, no truncation, field-keyed errors and atomic rollback. Twelve regression methods authored for boundaries, edit rollback, source/snapshot validation, partial-batch prevention, model limits/errors, whitespace/Unicode and authorization. New helper/test modules syntax/compile checked only; Django/Ruff/drift/PostgreSQL/CI NOT RUN by author. No newly observed baseline failing run/production oversized write claimed. No model/migration/auth/feedback/cancel/progress/archive changes. Guide: LESSON_LIBRARY.md.

## Merged work still awaiting acceptance
Skip-link PR7 merged ff2f68c1e67b6a24d3d8a6854f6187b3f89e49b6, guarded319b980; pre-merge runs45085015833/45085254574 independently successful, no passing count. Owner reports merge CI success19:24 EST without run/testedSHA/runtime/count. Actual browser focus/next-Tab/visual/no-JavaScript acceptance open. BUG003 REVIEW; PR6 merged7a82d69, head checks45082944989/45083255954 successful, browser/logging gates open. ROSTER-ASSIGN01 IN_PROGRESS; PR5 mergeda0cd91b, checks45081121549/45081792433 successful; A/B/stale/back/roster acceptance open. ASSIGN01/02 IN_PROGRESS; feedback staff-only, students status-only; progress history/reporting and durable token consumption absent.

## Failure history and boundaries retained
- UUID serialization: owner-supplied log296 tests/9 errors, run44667767312/f52a592; fixedddc000b, independently successful checks44668593439/44668981076.
- Feedback length: supplied log338 tests/2 failures from one test, c9b76e2/no runID; fixed23a9d2d, checks44846492681/44846822307 successful.
- Roster test: supplied log353 tests/one failure in13.113s, clean system check/exit1, run/revision unknown; incorrect anonymous405 expectation corrected83c86a3, later pre-merge checks successful. No failing total reused as a passing total.

Earlier CI/owner reports and BUG001/002/004/005/E05/E08 history remain in VALIDATION.json and linked prior ledgers. E08-05 IN_PROGRESS; existing owner-only attribution retained. Migration0003 deployment, Python3.14, browser/security/operations/file safety/student documents/audit/throttling/recovery/session/TLS/privacy/retention/mail/backup/training gates remain. No migration/credential/flag/deployment action or production authorization. Prior full ledger: https://github.com/pavanjains/lms/blob/ff2f68c1e67b6a24d3d8a6854f6187b3f89e49b6/docs/TICKETS.md
