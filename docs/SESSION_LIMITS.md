# Session limits (PROD-08, slice 1)

Owner decisions 2026-11-27: staff sessions end after 30 minutes without activity or 8 hours after the session started; student sessions end after 1 hour without activity (changed from 15 minutes) or 4 hours after the session started (unchanged). These are the owner's trial choices, not an approval of real-child access or of production use.

| Variable | Default | Meaning |
|---|---|---|
| LMS_STAFF_IDLE_SECONDS | 1800 | Staff idle limit. |
| LMS_STAFF_ABSOLUTE_SECONDS | 28800 | Staff absolute limit, never renewed. |
| LMS_STUDENT_IDLE_SECONDS | 3600 | Student idle limit. |
| LMS_STUDENT_ABSOLUTE_SECONDS | 14400 | Student absolute limit, never renewed. |

Each pair must satisfy 1 <= idle <= absolute <= 86400. Production refuses to start otherwise; a non-numeric value stops startup in every mode. SESSION_COOKIE_AGE is now 86400 (one day), an upper bound for any session that has no expiry of its own; before this change Django's default of two weeks applied to such sessions.

## How staff limits work
StaffSessionMiddleware (apps/accounts/middleware.py) keeps two timestamps in the session of a signed-in staff account: when the session started and when it was last active. The clock starts on the first request after sign-in, which is the page the sign-in redirects to. Only staff pages (paths under /account/ and /staff/) renew the idle time, so browsing the home page does not keep a session alive. The absolute time is never renewed. On every request the limits are checked; an expired, missing-in-part, non-numeric, out-of-order or future-dated clock signs the account out, and the next staff page redirects to the sign-in page. Timestamps up to 5 seconds in the future are tolerated for small clock differences between servers. The database session expiry is shortened to the time remaining.

Student limits work as described in STUDENT_SIGN_IN.md and are unchanged apart from the new idle default.

## Boundaries
- Limits are enforced on the next request, not by erasing a page already on screen. A screen left open stays visible until the next click.
- A sign-in that never makes another request keeps a session row until the one-day cap; the clock starts only at the first request.
- Existing signed-in staff sessions get a new clock on their first request after deployment.
- Owners do not have a separate, shorter idle limit; that was not requested.
- Re-authentication for sensitive actions, remember-me and per-device lists are not implemented.

## Verification status
The author could not run Django here. The clock logic passed seven tests in a sandbox with stubbed Django modules; the middleware and database tests (apps/accounts/test_staff_session_limits.py), the production startup tests (apps/core/test_production_session_limits.py) and the updated student expiry test have not been run by the author, so CI is the first real run. No browser check has been done.

## Manual acceptance
With staff sign-in enabled locally and short limits (for example LMS_STAFF_IDLE_SECONDS=60 and LMS_STAFF_ABSOLUTE_SECONDS=180):
1. Sign in as an owner with MFA, open a staff page, wait past the idle limit, click again and confirm the sign-in page appears.
2. Sign in again and click a staff page every 30 seconds; confirm the session ends at the absolute limit even though it was active.
3. Confirm that visiting the home page does not extend the idle time.
4. Confirm student sign-in still ends after the idle and absolute limits, with the 1-hour idle default when the variables are unset.
