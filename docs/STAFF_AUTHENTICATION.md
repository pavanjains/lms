# Staff authentication primitives — E04 prerequisite slice

## Implemented
- StaffEmailBackend: case-insensitive email/password authentication for active OWNER and INSTRUCTOR users in active organizations.
- Staff session lookup repeats role/account/organization checks.
- staff_mfa_required: denies protected requests unless the active staff account has a callable is_verified() returning true.
- Protected successful responses receive never-cache headers.
- Sixteen focused tests use synthetic accounts.

## Intentionally not enabled
This commit does not change AUTHENTICATION_BACKENDS, middleware, installed apps, dependencies, or URL routes. No password-only dashboard is exposed. The backend and guard are ready for integration, not an operational login feature. Student authentication will use a separate deliberately designed path; do not add an unrestricted fallback backend to staff login.

## Next integration
1. Resolve and review the django-two-factor-auth dependency and its transitive dependencies against Django 5.2; commit a lockfile.
2. Add django-otp TOTP/static devices, middleware, and library migrations.
3. Wire staff email authentication to the library login flow; label its identifier field Email.
4. Provide enrollment and one-time recovery-code workflows. Keep remembered-browser bypass disabled on center devices.
5. Apply staff_mfa_required to every staff business view; allow only the narrowly necessary authentication/enrollment routes before verification.
6. Add real OTP tests, including replay, invalid/expired token, recovery code reuse, enrollment, session invalidation, CSRF, and logout.
7. Add password-attempt throttling, monitoring, and approved session expiry before operational use.
8. Implement password recovery with tested mail configuration; never bypass MFA during recovery.

The guard alone is not class authorization. Class/resource policies must additionally protect class-specific records.

## Tests
```sh
python manage.py test apps.accounts.test_staff_access --settings=config.settings.test
# With the PostgreSQL environment exported:
DJANGO_SETTINGS_MODULE=config.settings.ci python manage.py test
```
MFA tests in this slice mock the verification predicate to test the access boundary; they do not validate an OTP library or prove an MFA flow works.

## Verification status
Python syntax checked during authoring. Django runtime tests, PostgreSQL, dependency resolution, CI status, and actual MFA are unverified. E04 authentication/MFA epics are not complete.

## References reviewed
- https://django-two-factor-auth.readthedocs.io/en/stable/installation.html
- https://django-two-factor-auth.readthedocs.io/en/stable/implementing.html
- https://django-two-factor-auth.readthedocs.io/en/stable/configuration.html
