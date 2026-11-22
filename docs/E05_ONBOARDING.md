# E05 instructor onboarding — development preview

Updated 2026-11-22 for BUG-003; branch fix/bug-003-onboarding-verification, baseline a0cd91b. BUG-003 remains REVIEW. Tests and procedures are not browser/logging/production acceptance.

## Flow and local preview
MFA-verified owner invites an instructor with explicit confirmation. Backend issues a one-time invitation and submits plain-text mail. Recipient sets username/password; server fixes role to INSTRUCTOR and organization to the invitation. Activation does not sign the user in. Completion links to staff sign-in/MFA enrollment.

Confirmed resend targets the stored recipient and invalidates old pending links. GET sends no mail and consumes no invitation. Signed-in users must sign out before activating another account.

Development console email prints links: use synthetic accounts only and keep output private. Both LMS_STAFF_AUTH_ENABLED and LMS_INSTRUCTOR_ONBOARDING_ENABLED are required. Development defaults: LMS_PUBLIC_ORIGIN=http://localhost:8000 and LMS_INVITATION_FROM_EMAIL=noreply@example.test. No flags/accounts/credentials/migrations are changed here. Do not rerun bootstrap on the existing installation; use development settings, never test/CI settings, for browser/account work.

Operational enablement requires approved HTTPS origin, sender, mail backend/credentials and release gates below. Origin is configured, never derived from request Host. HTTP is allowed only for loopback with DEBUG=true. Mail-backend acceptance is not inbox delivery.

## Delivery failure policy retained
Issue/replacement and synchronous mail submission share a database transaction. SMTP/OS errors or zero accepted messages roll back new invitations and replacement revocations. Do not automatically retry ambiguous delivery. Mail and database are not a distributed transaction: provider acceptance followed by commit failure can email an unusable link. Durable outbox/delivery audit remains open; no worker is added.

## BUG-003: current CSRF/privacy contract
Historical ledger records correction 24453d6 from no-referrer to same-origin, local confirmation on November 15 and later owner-reported included CI success; full browser acceptance remained open. Current onboarding.page sets Referrer-Policy: same-origin. The previous no-referrer wording in this guide was stale and is superseded.

Keep CSRF middleware/form tokens enabled. Origin checks must reject null/foreign origins even with a valid CSRF token and same-origin Referer. New HTTPS tests also cover secure same-origin Referer fallback when Origin is absent. Never trust null, broadly widen trusted origins or exempt these forms to bypass failures.

Onboarding pages use same-origin/no-store headers; passwords use sensitive-POST filtering and are not echoed. Headers/generic error pages do not redact token paths in logs or erase browser history.

## Browser checklist — NOT RUN for this increment
Use separate MFA-owner and signed-out browser profiles, synthetic fixtures and one consistent approved origin. Do not send real invitations or paste token URLs, passwords, cookies or OTP material into evidence. A loopback HTTP trial does not prove HTTPS behavior; HTTPS needs an approved test setup, not weakened TLS/proxy checks.

1. Normal confirmed owner invite/resend submissions succeed without the old null-origin CSRF failure; GET sends nothing. Resend cannot change recipient; old link fails and replacement works.
2. Signed-out activation GET does not consume the invitation. Inspect same-origin/no-store headers privately. Mismatched passwords show errors, do not echo passwords and leave the invitation usable.
3. Valid activation succeeds once with fixed INSTRUCTOR role/organization, does not sign in, and still requires staff sign-in/MFA. Used/expired/revoked links are unavailable. Signed-in activation asks for sign-out.
4. Check back/reload, validation/retry, duplicate-account/delivery prevention and already-rendered/BFCache privacy. No history-erasure guarantee is made.
5. Repeat normal submissions on approved HTTPS; inspect Origin/Referer locally if needed, without exporting token-bearing headers. Do not disable CSRF or mix host/scheme/port.
6. Record exact revision/runtime/browser/origin and PASS/FAIL/NOT RUN/BLOCKED per case, with attribution and no secrets. Simulated HTTPS request metadata is not actual browser/TLS/proxy acceptance. CI alone does not close BUG-003.

## Token-path logging gate — OPEN
Tokens remain in activation URL paths/history; console email intentionally prints them locally. Before operational enablement, inventory and privately verify redaction across Django/security/exception logs, WSGI server, hosting/proxy/CDN access/error logs, APM/error reporting, mail diagnostics and retained exports/backups. Review request targets, Referer and exception metadata. Application filtering alone cannot redact upstream captures.

Use synthetic markers and token-free evidence. No hosting topology/sink configuration is established, no production redaction filter is implemented, and no blanket log-safety claim is made. Throttling, audit, session/recovery, PostgreSQL races, delivery/privacy/retention and production approval remain open.

## Automated verification — NOT RUN by the author
Existing onboarding tests remain unchanged. New apps/accounts/test_onboarding_csrf_https.py adds 10 methods with enforce_csrf_checks=True, secure requests/cookies, SSL-redirect test settings and no trusted-origin additions. Coverage: HTTPS Origin/Referer success, invite/resend/activation rejection for null/foreign/scheme/port origins, missing/unsafe Referer, missing CSRF, one-time/no-auto-login behavior and validation/expired/revoked privacy headers. This is an authored-method count, not a passing total or infrastructure/logging proof.

In the isolated PostgreSQL test environment:

```sh
ruff check .
python manage.py check --settings=config.settings.ci
python manage.py makemigrations --check --dry-run --settings=config.settings.ci
python manage.py test apps.accounts.test_onboarding apps.accounts.test_onboarding_csrf_https --settings=config.settings.ci --verbosity=2
python manage.py test --settings=config.settings.ci --verbosity=2
```

Author checked new Python syntax/compilation only. Django/Ruff/rendering/browser/TLS/proxy/log-redaction/PostgreSQL verification NOT RUN; new CI pending. Initial 14-test authoring notes and earlier onboarding import failure/subsequent owner pass are historical, not a current total or new verification. No production authorization.
