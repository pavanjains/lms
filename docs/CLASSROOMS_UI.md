# E08-04 classroom browser UI

Status REVIEW. Code/tests authored, not run here; CI and browser acceptance pending. No new migration beyond E08-01. /staff/classes/ is linked from staff workspace.

## Behavior
Owners create classes, assign/remove instructors, enroll/end enrollment and archive. Instructors see only active assigned classes and may manage enrollment there, adding only already-visible students. Selectors use usernames to distinguish accounts, scoped to same organization and allowed operation. Removal selectors may include inactive accounts with retained active links, but do not expose unrelated accounts. No student account creation, reactivation, class edit, or historical roster export included.

All mutations have GET review plus confirmed POST. Forms never accept organization/creator/role; services reauthorize under transaction. Missing confirmation/forged target produces 400, unauthorized owner actions 403, inaccessible classes/unknown operations 404. Changed permissions may produce 403 at service time. Validation/database conflicts return generic form errors without leaking data. No CSRF exemptions or null-origin allowlisting. Responses use same-origin referrer policy and existing private/no-store staff protections.

Class list and active student roster paginate at 20; instructor list is not paginated. Archived classes visible to owner only, with no roster/membership controls. UI does not implement cleanup in archived classes even though backend owner services support it. Class description remains visible to authorized owner. No cross-class lessons/feedback exposed.

## Verify
```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test apps.classrooms --settings=config.settings.ci
python manage.py test --settings=config.settings.ci
ruff check .
```

Load local development environment, apply E08-01 migration if needed, explicitly enable staff auth locally, run server and sign in with MFA. Open http://localhost:8000/staff/classes/ .

1. Owner creates a synthetic class; unchecked confirmation must not save.
2. Assign two existing synthetic instructors; verify each sees only assigned classes.
3. Owner enrolls an existing synthetic student. Student creation UI is a later task; an empty student selector is expected if no eligible accounts exist.
4. Assign an instructor to a second class and verify they can enroll a student already visible through the first. An unrelated student must be absent/rejected.
5. End enrollment and remove an instructor; next request must reflect access loss.
6. Archive as owner; class disappears for instructors, owner detail omits roster, accounts/links retained.
7. Verify CSRF/origin protection and cross-organization IDs, keyboard navigation, form labels and pagination with synthetic data. Record revision/environment/results separately from CI.

Service/policy units and UI client tests do not replace real browser MFA, session and concurrent PostgreSQL acceptance (E08-05).
