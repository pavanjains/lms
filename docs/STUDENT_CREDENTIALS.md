# E08-07 student password reset and credentials

Status REVIEW; code/tests authored, not executed here. CI/browser/race acceptance pending. No new migration. This is staff-managed student reset only, not staff recovery or student sign-in.

## Flow / scope
From an active class roster, Review password reset shows student identity and username. Existing passwords cannot be recovered. GET does not change anything. Confirmed CSRF-protected POST rechecks MFA/current staff and class membership/enrollment, generates secrets.token_urlsafe(18), validates/hashes it and revokes target's unexpired database sessions in the same transaction. Owners also need the student actively enrolled in the selected class. Only active STUDENT accounts with profiles qualify.

Organization/actor/class/student locks follow existing service order. Session cleanup scans unexpired database sessions and removes matching auth user IDs only; staff/other sessions retained. Supported SESSION_ENGINE is django.contrib.sessions.backends.db only; cached_db, signed cookies and other engines rejected. Future student backend must also honor active role/status and password/session hash checks; concurrent sign-in and in-flight requests are not solved by these tests.

## Receipt and security limits
Success renders new credentials directly in the reset POST response. No redirect carrying secrets, no persistence in session/messages/email/URLs, no GET retrieval API. Password excluded from dataclass repr and error-report variables marked sensitive. Receipt has private/no-store cache controls, same-origin referrer policy, X-Robots-Tag and CSP restricting scripts/external resources/frames/forms. These controls do not erase history, screenshots, clipboard or copies; response-only display is not cryptographic once-only viewing.

Password is not auto-expiring, single-use or forced to change. Repeating POST resets again and invalidates the previously issued password. Returning via GET reveals no issued password. Lost receipt requires another confirmed reset. No bulk export/PDF/download/email/automated handout, student authentication or staff reset in scope. Use only synthetic credentials until TLS, privacy, durable audit, throttling and controlled delivery procedures are approved. Production logging must never capture receipt bodies.

Old E08-06 notes saying reset/handout are absent describe that earlier increment; reset plus response receipt are now authored here, not verified production delivery. No real password is changed by committing source.

## Verify
```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test apps.classrooms.test_credentials --settings=config.settings.ci
python manage.py test --settings=config.settings.ci
ruff check .
```

Synthetic browser checks: authorized instructor GET/cancel leaves password unchanged; unconfirmed POST fails; confirmed POST shows new credentials; GET cannot retrieve them; student/staff/org/class boundaries hold; only matching database sessions removed; instructor remains signed in; another reset invalidates prior password. Student sign-in still unavailable. Record actual revision/backend/results separately.

Further work: PostgreSQL reset/reset and reset/access-removal/create/login races, actual browser/session acceptance, credential UX for young students, audit/throttling/expiry policy and approved delivery. Existing E08-05 suite does not cover these new reset paths.
