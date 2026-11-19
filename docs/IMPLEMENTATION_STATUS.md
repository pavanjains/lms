# Implementation Status

Updated: 2026-11-18, 19:58 EST. docs/TICKETS.md tracks evidence.

## E08-04 authored
Classroom list/detail and confirmation forms for owner create/archive, instructor assignment/removal and scoped student enrollment/end-enrollment. Staff workspace links to classes. Existing staff middleware/MFA/private-cache controls apply under /staff/classes/. Views recheck current roles, resolve IDs through scoped policies, validate selector choices and use services for every mutation. Read-only GET; CSRF-protected POST; same-origin response policy.

Lists/active rosters paginated at 20; instructor names and roster context project safe fields, no complete User serialization. Class selectors never expose unrelated students. Archived owner detail retains description/status but omits roster and management controls; instructors cannot open archived/unassigned classes. No student creation, reactivation, new migration, runtime account/data change or flag activation.

UI tests authored, NOT RUN here. New CI/browser acceptance PENDING. Existing E08 service tests unchanged after review of method-level settings decorator. E08-02/03 7e3792c CI result still not supplied. E08-01 6929d69 CI_PASSED by owner November 15 15:50 report with run https://github.com/pavanjains/lms/actions/runs/43758274124 ; fetch failed, not independently verified, no count inferred. Local migration and manual acceptance not implied.

## Prior work and boundaries
[Previous full status](https://github.com/pavanjains/lms/blob/7e3792c115769739fc1a200db1bc366123a700b2/docs/IMPLEMENTATION_STATUS.md) preserves earlier slices/evidence. Foundation, staff/MFA, lifecycle, deactivation, origin fix, class models and services/policies remain implemented. BUG-001/002 verified by prior owner reports; BUG-003 local fix reported working, full browser checks pending. E05-07 manual deactivation/session verification pending.

E08-05 PostgreSQL races and browser acceptance next. Permission querysets are request-scoped, not reusable grants; direct ORM can bypass model validation and cooperating lock protocol. Student creation/initial instructor access, shared-device sessions, lessons/documents/assignments, progress/feedback/reports, deployment/restore/privacy/retention/audit/recovery/throttling/session/last-owner/mail/log-redaction/training and Python 3.14 CI remain incomplete. Flags remain off by default. Passing CI alone is not production approval.
