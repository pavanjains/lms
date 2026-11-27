# Assignment workflows

Updated 2026-11-22. Branch feature/class-roster-assignments; baseline 88524ab. ASSIGN-01/02 and ROSTER-ASSIGN-01 remain IN_PROGRESS. PROD-09 note added 2026-11-27 against main f010611d76b8487f4085e1a54fecc90e23b69e61. No production acceptance.

## Class-roster flow
1. Open an authorized active class. Select visible students; Select all means this page only. JavaScript updates count/disables empty submission and clears selection on navigation. Without JavaScript, select individual students; server rejects empty selections.
2. Continue with students preselected. Change recipients if needed, choose an active same-organization lesson and expand Preview available lessons for kit/grades/summary/instructions.
3. Review exact recipients and lesson snapshot/version. Grade/duplicate errors identify affected students; no silent removal or partial batch. Review alone creates nothing.
4. Check confirmation and press Confirm and assign. Existing service rechecks current staff/MFA, class/account/org/enrollment, lesson/version, grade/kit and duplicates. Revocation may return 403/404. Unreviewed posted recipients/lesson/origin cannot replace signed values.
5. Return to class with success count, unchecked roster and independently paginated class history/status/detail links. Central history and existing progress controls remain. Roster never renders feedback.

Change selection preserves valid choices and invalidates the old review. Cancel is a CSRF-protected POST clearing the current review. Stale/expired reviews require fresh review. Central-entry success still returns to central history.

Reviews remain actor/org/class/session bound, signed and valid for 900 seconds; latest review replaces earlier review. No durable exactly-once concurrent token store. One snapshot per explicit recipient, active class/student/lesson uniqueness, cancellation history and explicit reassignment remain. No automatic assignments for later enrollments. Students see status only, not feedback or write controls. Only latest staff progress/feedback is retained; migration 0003 deployment unverified. This feature adds no migration.

### Double confirmation and replay (PROD-09)
Duplicate active assignments are prevented independently of the token: the assignment_one_active_lesson unique constraint (class, student, lesson, not cancelled), row locks on the organization, class and lesson, and a duplicate check inside create_assignments. By code reading, a concurrent double confirmation cannot create two active copies; the losing request is shown Review expired or data changed. The review token is removed from the session only after the assignments are created and is not recorded as used in the database. Remaining window: if a concurrent request in the same session saves stale session data, the removed token could become usable again until it expires (at most 900 seconds), which could re-create assignments the instructor had cancelled in that time. That race cannot be triggered reliably in a test and is not closed; recording each token nonce in a table (a new migration) remains an option. Tests: apps/lessons/test_assignment_concurrency.py has six PostgreSQL ordered-race tests (double confirm, overlapping batch, cancel then reassign, double cancel, archive before confirm, confirm before archive) and two sequential replay tests. They are authored, not executed by the author, and CI is pending; no passing count is claimed.

## Verification procedure — NOT RUN by the author
Preserve local changes; use the feature branch and isolated PostgreSQL test settings. Do not rerun owner bootstrap or use production data. LOCAL_TESTING.md has environment setup.

```sh
ruff check .
python manage.py check --settings=config.settings.ci
python manage.py makemigrations --check --dry-run --settings=config.settings.ci
python manage.py test apps.lessons.test_roster_assignments apps.lessons.test_assignment_views apps.lessons.test_assignments apps.lessons.test_assignment_review_uuid apps.lessons.test_assignment_progress apps.lessons.test_student_views apps.lessons.test_assignment_concurrency --settings=config.settings.ci --verbosity=2
python manage.py test --settings=config.settings.ci --verbosity=2
```

15 authored regression methods cover preselection, exact signed confirmation/return, invalid recipients/lessons, grade/duplicate/no partial batch, change/cancel invalidation, checkbox/tampering, stale/revoked data, access/archive, history privacy/scope/pagination, CSRF/method guards, central return and expiry/replacement/session binding. This is not an executed passing count.

Browser gates: keyboard labels/count/select-page/indeterminate state; no-JavaScript fallback; 21+ student pagination; preview/error choice preservation; final Confirm; cancel/back/reload/replay; history/detail links; A/B isolation and status-only privacy. Use separate profiles and synthetic fixtures; record exact revision/runtime/results without tokens/credentials. Skip-link defect remains separate.

Owner-reported prior assignment/Confirm, progress/reload, privacy and CI on 88524ab are not new-flow acceptance. Earlier UUID failure (296 tests/9 errors) and feedback-length failure (338 tests/2 failures from one test) are retained in VALIDATION.json. Author has not run Django, Ruff, rendering, browser or PostgreSQL verification.

Prior detailed contracts/history:
https://github.com/pavanjains/lms/blob/88524ab8788fc61b72c2a4d8ff19ccbdee38d159/docs/ASSIGNMENTS.md

## Authentication-order regression and retest
Owner-supplied CI log: 353 tests in 13.113s, one failure, clean system check, exit 1 (run ID/revision/runtime not supplied). The test incorrectly expected an anonymous PUT to reach the view's 405 guard; StaffAuthMiddleware redirects to login first. The corrected test expects login redirects for anonymous/password-only sessions and 405 only after MFA, retaining CSRF assertions. No application guard is changed. Replacement-method syntax checked; rerun the targeted and full suites above. This failure is retained, not a passing-suite claim.
