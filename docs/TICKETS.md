# Development Tickets and Fix Ledger

Updated: 2026-11-18, 21:33 EST.

[Previous complete ledger](https://github.com/pavanjains/lms/blob/aa3d0d9ecf1049c15c411550058687b7b9ce471b/docs/TICKETS.md) preserves E01–E22/E08, LESSON-01, BUG and commit history. Unaffected statuses unchanged. REVIEW is authored, not passing/manual/production acceptance. No fabricated counts or independent Actions claims.

## Current
- BRAND-01 REVIEW: Stembotic shared header/title, inherited MFA pages, production error templates and generic CSRF failure page; tests authored. JSON health/downloads/debug/framework-generated non-template responses excluded.
- DOC-01 REVIEW: protected database-stored PDF support documents, migration, upload/list/attachment-download/archive UI, permission/size/quota/version/integrity checks and tests authored. Flag false by default. No students/assignments, scanning or public media. CI/migrations/browser/security/backup acceptance pending; NOT RUN here.
- LESSON-01 REVIEW at aa3d0d9; no CI result supplied.

Only lesson creator/owner mutates documents under fresh actor/MFA/org/lesson locks and expected parent version; active same-org staff visibility follows library policy. PDF max5 MiB, max20 active/lesson, org100 MiB includes archived bytes. Check extension, bounded actual reads, PDF header/end marker, SHA-256 integrity; not a safe-file guarantee. Store content/metadata in DB transaction, parent version increments; no filesystem orphan transaction. Forced attachment/octet-stream/nosniff/CSP, private/no-store. Archive hides downloads, retains BLOB/quota; no physical deletion/reactivation. Archived-lesson downloads only creator/owner, no document mutation there.

Security/production gaps: no antivirus/CDR/full PDF parser; request body may spool before view validation, infrastructure request limits needed; raw ORM bypass/parallel quota tests and durable audit open. No real user/file upload approved. New source commit changes no flags/runtime data/dependencies. Migration creates document table.

## Evidence / BUG carry-forward
Owner 21:18 CI passed after ded6acb, E08-08 CI_PASSED/BUG-004 FIXED_VERIFIED user-reported only, URL/count unknown/not independently retrieved. Preserve a372751 Ruff F401 one unused ClassInstructor import and ded6acb import-only fix retaining tests. E08-02/03/04/06/07 pass per prior owner all-CI report through 460d7fa. E08-05 IN_PROGRESS despite reported automated pass because browser/new races open. E08-01 older reported run43758274124 fetch failed/count unknown. New lesson/document increments not covered.

BUG-001/002 prior FIXED_VERIFIED evidence retained: 50 tests/four bootstrap errors/46 passed then owner pass; onboarding 83 entries/one import error/82 passed/no onboarding methods executed/fourteen retained, later e3bcfcb pass without count. BUG-003 remains REVIEW for full browser acceptance despite local fix and included CI report; token-path logging work open. Earlier E05/recovery/security/operational statuses preserved in linked ledger, not completed by branding/uploads.

Next assignment/student document policy, scanning/storage operations, existing account/shared-device/race/audit/throttling/privacy/deployment gates remain open.
