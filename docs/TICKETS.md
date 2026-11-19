# Development Tickets and Fix Ledger

Updated: 2026-11-18, 21:05 EST.

## Evidence/history
[Previous complete ledger](https://github.com/pavanjains/lms/blob/460d7fabe91df823f81766bd5d84756102679f3a/docs/TICKETS.md) preserves E01–E22, BUG and commit evidence. REVIEW means authored awaiting verification; CI_PASSED does not imply manual/production approval. Markdown IDs are not GitHub Issues.

Owner November 18 21:02 message: CI for all have passed. Applies through 460d7fa as confirmed in conversation, user-reported only, not independently retrieved; no new URL/count supplied. E08-08 is not covered.

| Ticket | Status | Evidence / remaining work |
|---|---|---|
| E08-01 | CI_PASSED | 6929d69 prior owner report with run 43758274124, fetch failed/count unknown. |
| E08-02/03 | CI_PASSED | 7e3792c included in November 18 owner report; manual/security gates open. |
| E08-04 | CI_PASSED | d437edf included in report; browser acceptance open. |
| E08-05 | IN_PROGRESS | 7f97933 concurrency CI passed per report; browser and newer-path race extensions open. |
| E08-06 | CI_PASSED | 873cbb4 included in report; creation browser/race acceptance open. |
| E08-07 | CI_PASSED | 460d7fa included in report; credential browser/race/operational limits open. |
| E08-08 | REVIEW | Student authentication/dashboard/expiry/isolation and tests authored, NOT RUN here; new CI/manual/races pending. |

E08-08: separately gated student backend uses student_username credential, no staff fallback or MFA bypass. Active student/profile/org and nonstaff flags required. Session timestamps enforce provisional idle/absolute limits; missing/malformed/expired session flushed. Single browser identity, switching requires logout. Staff attempts at student routes denied/preserved; students denied staff routes without silent logout. POST login/logout require CSRF; successful login flushes anonymous context, fixed destination, stores no password. Dashboard uses request user only and safe own profile/class names; no roster/descriptions/other student records.

Student login locks org/user and persists session inside transaction; sequential reset/hash-change invalidation tested. Simultaneous reset/login/save, all schedules, back/forward cache and browser boundaries still unverified. No new migration or runtime/flag activation. Student flag false by default, database session engine only. Staff flag unchanged. Student account with no active enrollment can sign in to empty class list; inactive account/org/profile cannot.

## Carry-forward/history
Unchanged security/operational tickets retain prior statuses. E05-07 and BUG-003 now have passing included automated-suite evidence by owner's all-CI report, but manual acceptance remains open; BUG-003 stays REVIEW until scoped browser acceptance is completed. E05 delivery/audit/throttling/races and staff recovery/last-owner/session controls remain open. No claim of separate historical run verification.

BUG-001/002 FIXED_VERIFIED by earlier owner evidence. BUG-001 ef6b96c: 50 tests/four errors/46 passed before correction, owner pass 08:24 November 15. BUG-002 1b4a5dd import corrected e3bcfcb: 83 entries/one import error/82 passed, no onboarding methods executed; fourteen retained; owner pass 13:28 without count. BUG-003 24453d6 local null-origin fix confirmed November 15 15:07; full browser acceptance open, token logging work remains. Earlier commit/range evidence retained in linked ledger. No new passing counts inferred; no independently retrieved Actions claims.

New E08-08 CI PENDING, SHA assigned at commit. Browser acceptance, rate limiting, audit, TLS/privacy/log redaction, credential UX and Python 3.14 support not completed by prior CI.
