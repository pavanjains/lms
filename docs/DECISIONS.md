# Decision register

## Approved
- Django, PostgreSQL, private S3-compatible documents.
- One owner, five instructors, 25 students initially.
- Individual student credentials, no student email required.
- Class-scoped teaching permissions and shared instructors.
- Essential through Grade 4; Prime Grades 4–8.
- Version-pinned lessons; instructors control progress and feedback.

## Proposed implementation choices
| Decision | Proposal | Status |
|---|---|---|
| Runtime | Python 3.12; Django 5.2 release family | Proposed; compatibility/security verification pending |
| Username | Globally unique; student-facing display name separate | Proposed |
| Staff email | Case-insensitive unique across staff accounts | Proposed |
| Student grade | Pre-K, K, 1–8; does not imply kit | Proposed lower-bound representation |
| Student profile creation | Service must call full_clean; role linkage not a DB cross-table constraint | Service not implemented |
| Sessions | Student idle 15 min; absolute 8 hr; staff idle 30 min | Proposed, NOT implemented |
| Documents | PDF, JPEG, PNG; 10 MB each | Proposed, NOT implemented |
| Retention | Owner-approved schedule before launch | Open |
| Hosting, privacy, consent, recovery | Resolve before production | Open |

Django framework is_staff/is_superuser flags are not the LMS role or MFA. No staff routes are enabled in this slice. Do not enable admin or classroom routes without explicit authorization and MFA work.
