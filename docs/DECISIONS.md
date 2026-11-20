# Decision register

Updated: 2026-11-20; reconciled against main 0d445e2 plus branch feature/assign-01-student-ui. Implemented does not mean production-approved or independently browser-accepted. The student assignment pages are authored (REVIEW), not merged.

## Product requirements retained
- Django/PostgreSQL; one STEM owner, five instructors and 25 students initially.
- Individual student credentials, no student email; shared devices require sign-out/account isolation.
- Organization/class-scoped permissions and shared instructors; no permanent creator ownership of students.
- Essential through Grade 4, Prime Grades 4-8; Grade 4 may use either, selected by instructor through lesson kit.
- Students read assigned learning content; instructor-controlled progress/feedback. No student submissions or student-controlled completion.

## Implemented choices and remaining approval
| Area | Current implementation | Remaining boundary |
|---|---|---|
| Runtime | CI Python3.12/PostgreSQL16, Django5.2 range; pyproject Python>=3.12,<3.14 | Reviewed resolved dependency lock/security process; no Python3.14 support claim |
| Identity | Globally unique username, separate display name; staff email case-insensitive uniqueness; minimal student profile | Credential-delivery/privacy/recovery approval |
| Grade | PRE_K/K/1-8 profile strings; -1/0/1-8 lesson integers; assignment conversion | No kit inferred from grade alone at Grade4 |
| Authorization | Fresh staff/MFA/org and current class policies, transactional validated services | Raw ORM bypass/cross-table consistency not DB authorization; audit/throttling remain |
| Student sessions | DB backend; provisional idle900s/absolute14400s, server checks on request | Production policy/browser/race approval; not original 8-hour proposal |
| Staff sessions | Mandatory MFA on business routes; remembered bypass/self-disable blocked | Approved idle/absolute policy, recovery/throttling/audit |
| Assignments | Explicit recipient snapshots; source version checks; retained versioned cancellation; org UUID normalized in JSON token. Student read-only list/detail authored on the student-UI branch with an availability-only Assigned label | Student pages merge/browser acceptance, instructor progress/feedback, concurrent durable token consumption |
| Documents | Gated PDF-only private database BLOBs;5MiB/file,20 active/lesson,100MiB/org incl.archives | Original private S3-compatible target is not current storage; DB choice is a documented implementation deviation, not a newly approved production architecture. Scanning/parser/CDR/request limits/restore/retention review required |
| Delivery | Gated onboarding with development console email | Production mail/outbox/redaction/retention/security acceptance |

Older PDF/JPEG/PNG10MB and student8hr/staff30min entries were proposals, not implemented/approved behavior. Student profile validation services, staff integration and class routes now exist; their original future-work notes are historical. Retention, hosting, consent/privacy, backups/restore and recovery remain release gates. No launch approval follows from CI. The student pages add no flag, migration or setting.

[Previous decision register](https://github.com/pavanjains/lms/blob/92ed0ab127149081483c8044ab41cf4e4ee9f82e/docs/DECISIONS.md) preserves original proposals and approved target wording.
