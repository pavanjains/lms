# E08-06 instructor-managed student creation

Status REVIEW: authored, not executed here. CI/browser acceptance pending. No migration required beyond E08-01. This is a creation/enrollment slice, not student sign-in.

## Flow
Staff with MFA open an active authorized class, choose Create student, enter unique username, minimal display name, grade and matching password, then confirm. Owners may use any same-organization active class; instructors need current active membership. Account/profile/enrollment save together or roll back together. Existing enroll_student visibility restriction is not weakened: this separate creation service establishes initial access in a class already authorized.

Fixed organization/role/privilege fields cannot be posted. No student email collected. Password validated with configured validators, stored via set_password hash, never placed in messages/session/response URLs. Password fields have render_value=False and new-password autocomplete; all POST fields sensitive for Django error reporting. This does not replace production log-redaction policy, TLS, privacy review or operational controls. Use only synthetic accounts until approved.

Initial access is class-based, not permanent ownership by creator. All assigned instructors share access. Removing enrollment/membership or archiving class removes that scope unless another active authorized class grants it. No account deletion, creator relation, audit migration or ability to create unassigned students. Global case-sensitive username uniqueness follows existing User model; no availability API, generic conflict response does not disclose existing account/organization.

Creation is not idempotent: replay with same username fails generically without another account. Existing organization/actor/class locks serialize cooperating writes; database username uniqueness handles conflicts across organizations and IntegrityError rolls back. This new service has not yet had PostgreSQL race acceptance; E08-05 existing tests cover earlier enrollment services only. Privileged raw ORM writes can bypass service checks.

No student login endpoint, password recovery/reset, plaintext credential handout, forced-first-change or notifications introduced. Creating accounts does not authenticate students or replace instructor session. Test passwords must not be reused for real users.

## Verify
```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test apps.classrooms.test_student_creation --settings=config.settings.ci
python manage.py test --settings=config.settings.ci
ruff check .
```

With local staff auth explicitly enabled and synthetic data:
1. Owner creates class and assigns two instructors.
2. Instructor opens class and Create student; GET/cancel/unconfirmed POST must not create anything.
3. Confirm creation; student appears with grade, both assigned instructors see it, unassigned instructor does not.
4. Try invalid grade, weak/mismatched password and duplicate username; no partial records or password reflection.
5. Remove membership/end enrollment; verify access changes.
6. Try unrelated/archived/cross-organization class IDs and CSRF violations; reject without creation.
7. Verify instructor remains signed in; student cannot use staff authentication. Student sign-in awaits its own increment.

Record revision/environment/results separately from CI; never infer execution or counts from authored methods.
