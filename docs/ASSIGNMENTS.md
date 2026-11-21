# ASSIGN-01 — current assignment behavior

Baseline: foundation PR #1 merged at 9012dd1; instructor UI/BUG-006 PR #2 merged at 92ed0ab; student read-only pages PR #3 merged at 4695e7d. Instructor progress and feedback (ASSIGN-02) is on branch assign-02-instructor-progress and is not merged. Whole feature IN_PROGRESS; merged code is not complete browser/concurrency acceptance. Local steps are in LOCAL_TESTING.md.

## Instructor workflow
Open /staff/lessons/assignments/ from the lesson library. Choose an authorized active class, an active same-organization lesson and explicit enrolled students. Review lesson fields/source version and recipients, then explicitly confirm. Review alone/GET creates no assignments. Whole selected batch must satisfy active account/org/class/enrollment, fresh staff/MFA/class authority, grade/kit and expected lesson-version checks. Essential supports through Grade 4; Prime Grades 4-8; Grade 4 accepts either kit selected through the lesson. Pre-K/K profile strings map to lesson integers -1/0.

Review is signed, actor/org/class/session bound and expires after 900 seconds. Organization UUID is stored/compared as a string (BUG-006); other ID contracts unchanged. Most recent session review replaces earlier review; successful confirmation normally consumes it. There is no durable exactly-once nonce store under concurrency; do not claim cross-request idempotency beyond the active-assignment uniqueness protection.

## Progress and feedback (branch, not merged)
On an assignment detail page an authorized instructor or owner can set a progress status (Assigned, In progress, Reviewed, Needs revision) and optional feedback up to 2000 characters. Saving is a confirmed POST to /staff/lessons/assignments/<id>/progress/ with the current assignment version. The service locks the actor, assignment and active class, rejects stale versions, cancelled assignments and archived classes, records the updater and time, and advances the version. Any status may follow any other; students cannot change status. Feedback is staff-only. History of earlier values is not kept beyond the latest status and feedback; reporting is not implemented. The database rejects unknown status values and an update time without an updater.

## Stored content and history
One snapshot per explicit recipient stores original lesson FK/version, title, summary, LEGO URL, instructions, kit and grade range. Later lesson edit/archive does not silently rewrite assigned content. Later class enrollment does not create work automatically. One active classroom/student/lesson assignment allowed; duplicate active assignments reject the batch.

Staff list/detail follow current classroom authority. Cancellation requires authorized confirmed POST and current assignment version; actor/time/history retained, later explicit reassignment permitted. Only owner may cancel in archived classes. No submissions or student-controlled completion.

## Student workflow (merged, acceptance pending)
/students/assignments/ and /students/assignments/<id>/ show only the signed-in student's own uncancelled, currently eligible snapshots, using the existing student_assignments query and student session guard. On the ASSIGN-02 branch they also show the instructor-set status label; they never show feedback. No roster, documents, or write controls. See STUDENT_ASSIGNMENTS.md.

Use validated services. Direct ORM authorization/cross-table semantics and snapshot immutability are not enforced by database row-level policy; privileged bypass is outside the supported write path. Progress history and reporting, and assignment-aware student document authorization, remain separate work.

## Verification history
Pre-merge foundation checks independently retrieved successful. Initial UI f52a592 failed in reported run 44667767312; supplied log showed 296 tests,9 errors with UUID JSON serialization failure. Retain that failure; do not infer a passing count. Fix ddc000b changed payload and comparison consistently and added two UUID regressions, retaining prior tests. Checks jobs for push 44668593439 and PR 44668981076 independently retrieved successful before PR #2 merge. Test totals were not independently retrieved.

For the student pages, 18 HTTP test methods exist; checks 44834522871 and 44834596308 on the PR #3 head ebdb9ea were independently retrieved as successful (no test count). The owner reports CI succeeded for 4695e7d, a034438 and 5762135; not independently retrieved. ASSIGN-02 adds 22 test methods that were syntax-checked only; Django tests, migration check, Ruff, template rendering, browser and PostgreSQL race checks were NOT RUN by the author and no CI exists for the branch yet. Real browser selection/review/confirmation/cancellation/progress/MFA/cache/CSRF acceptance, student A/B browser checks and assignment/session concurrent interleavings remain open. No runtime database migration or deployment was performed.
