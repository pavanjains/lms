# Documentation index and current-scope guide

Updated: 2026-11-19; baseline main 92ed0ab.

## Current sources of truth
1. LOCAL_TESTING.md: operator-reviewed local setup, automated checks and synthetic browser procedures; not execution evidence.
2. IMPLEMENTATION_STATUS.md and ../ACTION_PLAN.md: current scope, next work and acceptance gates.
3. TICKETS.md and VALIDATION.json: attributed CI/failure/verification evidence.
4. ASSIGNMENTS.md and DECISIONS.md: current assignment behavior and decisions versus proposals.

Earlier feature guides below record their original increments. Their authored-method counts and authoring-time NOT RUN/pending statements are historical, not current CI totals. Statements such as no login/reset/assignments or future UI mean not included in that increment. The current scope and evidence above supersede those temporal limitations; they do not waive unchanged safety/authorization requirements. Do not execute an older guide's verification command against an unreviewed/shared/production database. Use LOCAL_TESTING.md first.

## Feature references and reconciliation
| Guide | Current interpretation / later changes |
|---|---|
| OWNER_BOOTSTRAP.md | Bootstrap command/protections retained; staff login/MFA implemented later. Use synthetic local email rather than its real-owner installation example for tests. |
| STAFF_AUTHENTICATION.md | Primitive/service history; integrated gated MFA now exists. |
| STAFF_MFA_INTEGRATION.md | Staff integration details; later onboarding/classes/student backend supersede original missing-feature notes. |
| INSTRUCTOR_INVITATIONS.md | Invitation service history; E05_ONBOARDING.md added delivery/activation/screens. |
| E05_OWNER_MANAGEMENT.md | Initial lists/revocation; onboarding and deactivation added later. |
| E05_ONBOARDING.md | Gated console-mail development trial; current referrer policy is same-origin after CSRF fix, not its older no-referrer wording. |
| E05_DEACTIVATION.md | Owner-controlled instructor deactivation/session cleanup; recovery/reactivation/audit remain open. |
| CLASSROOMS.md | Schema history; services/policies/UI implemented in later guides. |
| CLASSROOMS_ACCESS.md | Current organization/class-scoped policy/service semantics; UI now exists. |
| CLASSROOMS_UI.md | Browser class workflow; student creation/reset now exist separately. |
| CLASSROOMS_CONCURRENCY.md | Existing deterministic PostgreSQL classroom scenarios; not assignment/token or all auth races. |
| STUDENT_CREATION.md | Creation/enrollment security; password reset and sign-in implemented later. |
| STUDENT_CREDENTIALS.md | Staff reset/receipt policy; gated student backend now exists. |
| STUDENT_SIGN_IN.md | Session isolation and browser acceptance; current student home still identity/grade/classes only. E08-08 prior CI pass is user-reported; browser gates remain. |
| LESSON_LIBRARY.md | Library validation/access; supporting PDFs and instructor assignments added later. Grade mapping and snapshot decisions now implemented in assignment services. |
| LESSON_DOCUMENTS.md | Private staff PDF behavior/risks; uploads default off and student delivery absent. CI history updated in current ledger, not proof of real-file safety. |
| ASSIGNMENTS.md | Current merged foundation/instructor UI and remaining student/concurrency work. |

## Maintenance contract
Implementation/fix commits update all three tracking docs plus affected current guides, setup commands, decisions and validation evidence. Do not silently turn an old plan/proposal or authored test count into verified behavior. Preserve historical failures and source revision links. When working on an older feature guide, reconcile its temporal wording against this matrix and the actual code. A guide is not production authorization.
