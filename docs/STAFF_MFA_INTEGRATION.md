# Staff MFA integration — development preview

## Included
Staff email login, authenticator-app TOTP setup, library-managed recovery codes, POST logout, a minimal verified staff workspace, and mandatory verification on /staff/ and protected /account/ routes. No class data is exposed. Self-service MFA disable and remembered-browser bypass are disabled. No password reset/invitation flow is added yet.

Uses django-two-factor-auth 1.18.1 with django-otp. The phonenumberslite dependency satisfies upstream imports; phone/SMS plugins are not enabled. Existing backend and MFA guard are reused. All ordinary staff routes use /staff/; additional routes outside these prefixes must explicitly apply the same checks.

## Release gate
LMS_STAFF_AUTH_ENABLED defaults to false. Account and staff routes return 404 until enabled. The dependencies and middleware still load, and library migrations must still be applied. Enable only for local/staging verification until outstanding controls are complete.

```sh
python -m pip install -e '.[dev]'
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test --settings=config.settings.test
# Export this only for local/staging manual verification:
export LMS_STAFF_AUTH_ENABLED=true
python manage.py runserver
```

After owner bootstrap, visit /account/login/, sign in using the owner email, enroll an authenticator, verify its code, and store recovery codes privately. /staff/ requires verified MFA. Sign out using the POST form. No additional owner privileges, superuser account, or admin route are created by this change.

## Safety and pending work
- Runtime dependency resolution, reviewed lockfile, migration checks, and all tests must pass before claiming completion.
- Fifteen integration tests are authored, including real TOTP enrollment/login, replay rejection, and one-time recovery tokens. They have not been executed in the authoring environment.
- Password-attempt throttling and approved idle/absolute session limits are release blockers. Library token protections do not replace password throttling.
- Password/MFA recovery runbooks, staff invitation flow, authentication audit/monitoring, and full browser UAT remain unfinished.
- Recovery-code tests verify token consumption directly; a complete recovery-login browser scenario remains required.
- Add deterministic clock-boundary/expired-token and authentication-wizard timeout tests.
- Review OTP secret/recovery-code storage and database/backup access policy before production.
- Settings activate only StaffEmailBackend; student authentication is not yet available. Do not add an unrestricted fallback to enable students.
- Existing documentation describing disabled integration is superseded by this document for this slice; do not interpret it as a production approval.

## Source reviewed
Upstream 1.18.1 installation instructions, URL definitions, login/setup views, and form definitions in jazzband/django-two-factor-auth. No library internals are copied into the project; subclasses and documented integration points are used.
