# Documentation index and current-scope guide

Updated 2026-11-22 for branch fix/skip-to-content, baseline main 6e3dd23. PR #5 roster assignments and PR #6 BUG-003 verification are merged; acceptance remains pending. The skip-link change is authored on its branch, not verified or merged. The in-app Help manuals row was added 2026-11-25 against main 71b3d066bd818f883116d03869cc8ca091982656.

## Current sources of truth
1. LOCAL_TESTING.md: operator-reviewed local setup, automated checks and synthetic browser procedures; not execution evidence.
2. IMPLEMENTATION_STATUS.md and ../ACTION_PLAN.md: current scope, next work and acceptance gates.
3. TICKETS.md and VALIDATION.json: attributed CI/failure/verification evidence.
4. SKIP_LINK.md: current skip-link change, structural-test limits and keyboard/browser acceptance procedure.
5. ASSIGNMENTS.md, STUDENT_ASSIGNMENTS.md and DECISIONS.md: assignment behavior and decisions versus proposals, subject to later tracking/validation updates.

Earlier feature guides record their original increments. Authored-method counts and authoring-time NOT RUN/pending statements are historical, not current CI totals. Statements such as no login/reset/assignments or future UI mean not included in that increment. Current scope/evidence supersedes temporal limitations, not safety/authorization requirements. Do not execute an older guide against an unreviewed/shared/production database. Use LOCAL_TESTING.md first.

## Feature references and reconciliation
| Guide | Current interpretation / later changes |
|---|---|
| OWNER_BOOTSTRAP.md | Bootstrap protections retained; staff login/MFA added later. Do not rerun on the existing installation; use synthetic local fixtures. |
| STAFF_AUTHENTICATION.md | Primitive/service history; integrated gated MFA now exists. |
| STAFF_MFA_INTEGRATION.md | Staff integration; later onboarding/classes/student backend supersede original missing-feature notes. |
| INSTRUCTOR_INVITATIONS.md | Invitation service history; E05_ONBOARDING.md added delivery/activation/screens. |
| E05_OWNER_MANAGEMENT.md | Initial lists/revocation; onboarding and deactivation added later. |
| E05_ONBOARDING.md | Current same-origin guidance and HTTPS/CSRF verification from PR #6; browser/token-path logging acceptance open. |
| E05_DEACTIVATION.md | Owner-controlled instructor deactivation/session cleanup; recovery/reactivation/audit remain open. |
| CLASSROOMS.md | Schema history; services/policies/UI added later. |
| CLASSROOMS_ACCESS.md | Current organization/class-scoped service semantics; UI exists. |
| CLASSROOMS_UI.md | Class workflow; student creation/reset and PR #5 roster assignment added separately. |
| CLASSROOMS_CONCURRENCY.md | Deterministic PostgreSQL classroom scenarios, not all assignment/token/auth races. |
| STUDENT_CREATION.md | Creation/enrollment security; reset and sign-in added later. |
| STUDENT_CREDENTIALS.md | Staff reset/receipt policy; gated student backend exists. |
| STUDENT_SIGN_IN.md | Session isolation/browser acceptance; student home links to assignments. E08-08 prior pass is owner-reported. |
| STUDENT_ASSIGNMENTS.md | Merged read-only own assignments; staff-set status only, never feedback or write controls. |
| LESSON_LIBRARY.md | Validation/access; documents and assignments added later. Grade mapping/snapshots implemented. |
| LESSON_DOCUMENTS.md | Staff PDF behavior/risks; uploads restricted, student delivery absent. CI is not real-file safety. |
| ASSIGNMENTS.md | Snapshot/instructor/student flows plus PR #4 staff progress/feedback and PR #5 roster entry; browser/history/reporting/concurrency gates remain. |
| SKIP_LINK.md | New shared target focusability/outline fix and six structural regression methods; native browser focus/next-Tab acceptance NOT RUN. |
| In-app Help manuals (templates/help/owner.html, instructor.html, student.html) | Owner, instructor and student manuals shown under a Help tab: /staff/help/ for owners and instructors and /students/help/ for students. Written from the screens present at main 71b3d06; update them whenever those screens change. Wording and browser review open. Not a substitute for LOCAL_TESTING.md operator procedures. |

## Maintenance contract
Implementation/fix commits update action/tickets/status, affected guides/index and validation. Never turn proposals/authored counts into verified behavior. Preserve failures and source revision links. Reconcile older guides with actual code/current evidence. No guide or CI pass is production authorization.
