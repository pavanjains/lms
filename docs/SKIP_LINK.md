# Skip-to-content fix and browser acceptance

Branch fix/skip-to-content; baseline 6e3dd234417f831acd3a5362cad3adb0e4fb6d84. Owner reported the link did nothing on all pages. Source inspection found href="#main" and a matching main ID, but no tabindex or focus indicator. This is a source-level focusability gap, not an independently reproduced browser root cause.

## Change
Shared templates/base.html retains the visible, first native fragment link and adds class skip-link, tabindex="-1" on main and explicit focus outlines on the link/target. Main is a focus destination without being an extra sequential Tab stop. No JavaScript, autofocus, positive tabindex, route, authorization, form, session, credential, feature-flag or database change. Native fragment behavior is preserved, including with JavaScript disabled. Short pages may not visibly scroll; focus and subsequent Tab behavior must be checked, not scrolling alone.

Six new test methods in apps/core/test_skip_link.py check rendered structure across public entry pages, authenticated staff workspace/roster/assignment pages, student home/own assignments, error templates and real 403/404 responses. They check one matching main target, tabindex=-1, first eligible link ordering and explicit focus styles. Static/HTTP markup checks do NOT establish actual browser focus, next-Tab behavior, visual appearance or assistive-technology acceptance.

## Verification — pending
Author checked Python syntax/compile and parsed the authored base HTML structure with the standard library only. Django/Ruff/template rendering/browser checks NOT RUN by the author. CI pending; no passing count or FIXED_VERIFIED claim.

In an isolated test environment:

```sh
ruff check .
python manage.py test apps.core.test_skip_link apps.core.test_branding --settings=config.settings.ci --verbosity=2
python manage.py test --settings=config.settings.ci --verbosity=2
```

## Browser procedure — NOT RUN
Preserve local changes. Use the intended feature revision and development settings with synthetic accounts, never test/CI settings for account/browser work; do not rerun bootstrap. Keep staff/student profiles separate and security guards enabled.

1. On public home, staff sign-in and student sign-in, use Tab from the document start. Skip to content must be the first link reached with a visible outline.
2. Activate it with Enter. Confirm main actually receives focus and a visible outline, with URL fragment #main; scroll position alone is not evidence. Check both short and long pages.
3. Press Tab again. The next eligible control must be in main, not in the skipped header or back on the skip link. Main must not become an extra ordinary Tab stop. On a page without controls in main, record the applicable behavior rather than inventing a next control.
4. Repeat on authenticated staff workspace, roster, lesson/assignment pages, student home/own assignment pages, MFA setup and available branded error pages. Don't bypass MFA/authorization to reach pages.
5. Repeat with JavaScript disabled, then pointer activation and repeated activation/back/reload. Verify normal links/forms, roster selection and authentication remain unchanged.
6. Record browser/version, OS, revision and keyboard/focus/next-Tab/outline results separately; include an approved assistive-technology check where available. Test relevant supported browsers; do not generalize a single browser pass to all pages/browsers.

Mark cases PASS/FAIL/NOT RUN/BLOCKED with attribution. Redact credentials, cookies and invitation/review tokens. This is separate from BUG-003 and migration 0003. Acceptance remains pending until observed; no production approval.
