# Implementation Status

Updated: 2026-11-18, 21:33 EST. Evidence: docs/TICKETS.md.

## BRAND-01 / DOC-01 authored
Stembotic company name in shared header/title (brand outside title override block), inherited MFA and app-rendered pages. Branded production error templates and generic CSRF failure view. JSON liveness unchanged; downloaded source documents/debug/framework responses not rewritten.

New apps/documents stores PDF content privately in database with lesson/uploader/title/original-name/size/checksum/active/archive timestamps. Upload/archive creator or owner only; download through authorized staff route and library visibility, forced attachment/octets/nosniff/CSP/private caching. No public file URLs or student document access. Lesson version increments guard stale forms and serialize quota mutations under organization/lesson locks. Limits5 MiB/file,20 active/lesson,100 MiB/org including archives. BLOB transaction avoids external-storage orphan writes; larger database/restore cost requires review.

Only PDF extension/header/end-marker and SHA-256 checks, not antivirus/CDR/full PDF parsing. LMS_LESSON_DOCUMENTS_ENABLED defaults false; synthetic local testing only. Upload body can spool before application checks, so infrastructure body/rate limits and scanning needed before real files. Archived bytes retained/quota counted; retention/deletion and object-storage migration not implemented.

Tests/migration/drift/lint NOT RUN here; new CI/browser/security/backup/concurrency acceptance PENDING. Adds document migration, no dependency/flag activation/runtime data/email actions. LESSON-01 aa3d0d9 CI result not supplied.

[Previous full status](https://github.com/pavanjains/lms/blob/aa3d0d9ecf1049c15c411550058687b7b9ce471b/docs/IMPLEMENTATION_STATUS.md) preserves foundation/auth/class/student/lesson and BUG history. ded6acb CI passed per owner21:18, not independently retrieved/count unknown; BUG-004 FIXED_VERIFIED/E08-08 CI_PASSED. Earlier failures and prior owner reports retained; no new passing counts inferred.

Assignments/progress/feedback/student read-only lessons/reporting next. Scanning/request limits/storage restore/audit, existing shared-device/browser/races/throttling/recovery/session/last-owner/TLS/log-redaction/privacy/mail/dependencies/Python3.14/deployment/training remain release gates. No production authorization.
