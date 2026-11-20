# Stembotic Robotics LMS

Django LMS for one STEM owner, five instructors and 25 students initially. Development implementation, not approved for real-child or production use. Documentation baseline: main 4695e7d, which includes the student read-only assignment pages merged by PR #3; browser and concurrency acceptance for them is pending.

## Start here
- [Local setup, automated checks and browser testing](docs/LOCAL_TESTING.md)
- [Documentation index and historical-guide rules](docs/README.md)
- [Current implementation and verification](docs/IMPLEMENTATION_STATUS.md)
- [Action plan](ACTION_PLAN.md), [ticket/fix ledger](docs/TICKETS.md), [decision register](docs/DECISIONS.md)
- [Assignment workflow](docs/ASSIGNMENTS.md), [student assignment pages](docs/STUDENT_ASSIGNMENTS.md)

## Implemented
Owner bootstrap; gated staff email login/MFA and instructor onboarding/management; organization/class-scoped memberships; staff student creation/password reset; separately gated student sign-in/session isolation; lesson library; gated private PDF support documents; assignment snapshots/services and instructor selection/review/confirmation/list/detail/cancellation screens.

PR #1 merged foundation at 9012dd1. PR #2 merged instructor UI and BUG-006 at 92ed0ab. PR #3 merged the student pages at 4695e7d: student home links to read-only assigned-lesson list and detail pages showing the student's own eligible lesson snapshots (GET and HEAD only; no roster, documents or controls). "Assigned" only means available; it is not progress tracking. Student submissions and student-controlled completion are not product requirements. Instructor progress/feedback and reporting remain to build.

## Development
Use Python 3.12 and PostgreSQL 16 to match CI. pyproject.toml permits Python >=3.12,<3.14; that is not CI verification of every permitted version. Python 3.14 is not established as supported. Dependencies are range-constrained, not a reviewed resolved lockfile.

Follow LOCAL_TESTING.md for environment export, local-only feature gates, migration checks, owner bootstrap and MFA. Use development settings for browser accounts/server, never ci/test settings with their fast password hasher. Do not substitute createsuperuser for the LMS bootstrap. No admin route is enabled.

## Verification and safety
Pre-merge checks for dddb545, ddc000b and the PR #3 head ebdb9ea (runs 44834522871 and 44834596308) were independently retrieved as successful; no test counts are available from that source. Post-PR #1 main run 44665898145, the documentation commit 0d445e2 and the push of student-page tests 248127c passed CI per owner only. CI for merge commits after PR #2 and PR #3 has not been verified here. The student pages have 18 test methods, but the author checked only syntax and compilation. No test totals inferred. Browser, new assignment/session concurrency and production operations remain open. See docs/VALIDATION.json for attributed evidence.

Feature gates remain off by default. PDFs remain disabled outside controlled synthetic trials: signatures/integrity are not malware scanning. No deployment, runtime migration or credential action is performed by a documentation commit. Real-user readiness still requires security/privacy, audit/throttling/recovery, approved sessions, file safety, mail/deployment and backup/restore acceptance.
