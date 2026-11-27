# Production HTTPS settings

Added for PROD-04 (host-neutral part). These settings live in config/settings/production.py and are read from environment variables, so the same code runs on any host. All are optional, validated at startup (a bad value stops the server with a clear message) and default to the safe choice. Nothing here chooses a host, and nothing here has been verified on a real HTTPS deployment yet.

| Variable | Default | Meaning |
|---|---|---|
| LMS_HSTS_SECONDS | 0 (HSTS off) | Whole number from 0 to 31536000 (one year). Sets SECURE_HSTS_SECONDS. |
| LMS_HSTS_INCLUDE_SUBDOMAINS | false | true or false. Only takes effect when LMS_HSTS_SECONDS is above 0. |
| LMS_PROXY_SSL_HEADER | unset | Name of the request header, in Django's META form (for example HTTP_X_FORWARDED_PROTO), that the hosting proxy sets itself. Sets SECURE_PROXY_SSL_HEADER to that header with the value https. |
| LMS_CSRF_TRUSTED_ORIGINS | empty | Comma-separated HTTPS origins (scheme and host, optional port; no path, no wildcard). Sets CSRF_TRUSTED_ORIGINS. |

Existing settings are unchanged: debug off, secure session and CSRF cookies, HTTP-to-HTTPS redirect, a strong secret and explicit allowed hosts.

## HSTS rollout
HSTS tells browsers to refuse plain HTTP for the site for the stated time, so a mistake is hard to undo. Turn it on only after HTTPS works end to end. Start with a short value such as 300 (five minutes), confirm that sign-in, student sign-in and the Help pages work, then raise it in steps (for example one day, one week, one month, one year). Leave LMS_HSTS_INCLUDE_SUBDOMAINS off unless every subdomain of the domain is served over HTTPS. HSTS preload is never enabled by this code, because it cannot be withdrawn quickly.

## Proxy header
Most hosts terminate HTTPS at a proxy and forward plain HTTP to the app. Without a trusted header, Django sees every request as insecure and the HTTP-to-HTTPS redirect can loop. Set LMS_PROXY_SSL_HEADER only when the host's documentation confirms that its proxy always sets that header itself and replaces any value sent by the client; if it does not, anyone could send the header and make an insecure request look secure. When unsure, leave it unset and ask the host.

## CSRF origins
When the site is reached through a proxy or a custom domain, form posts can fail with an origin check error unless the site's own HTTPS origin is listed, for example LMS_CSRF_TRUSTED_ORIGINS=https://lms.example.org.

## Checking the result
After deployment, run manage.py check --deploy with the production settings and record the output. While LMS_HSTS_SECONDS is 0, expect the HSTS warning; it clears once a value is set. Browser checks that need the real host: the redirect from HTTP to HTTPS does not loop, sign-in works, the Secure flag is set on the session and CSRF cookies, and the Strict-Transport-Security header appears once HSTS is on.

## Not covered here
- Choice of host, domain and region.
- Serving static files in production (a host-specific choice; no static-file package is a dependency today) and the production server start command (gunicorn is already a dependency).
- Client IP handling behind a proxy, which the sign-in throttle (PROD-06) deliberately does not use.
- Scheduling the audit purge command (PROD-07, PROD-13), real mail (PROD-05), backups and monitoring (PROD-13).
