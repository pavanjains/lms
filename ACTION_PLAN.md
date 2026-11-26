# Robotics LMS — Action Plan

Updated 2026-11-26. Current branch docs/help-manuals-merge-status, baseline main c884396324318f3ca7be28e7b28423fb2acf326d (PR #14 merge). No production authorization.

## Current task
Record the HELP-01 merge (this documentation-only change; no code, settings, migration or model change). Next: the owner reads the owner, instructor and student manuals in a browser and corrects any wording that does not match the screens, then the remaining open acceptance items below.

## Recently merged
PR #14 merged at c884396: HELP-01 owner, instructor and student manuals as in-app Help pages with a Help tab (/staff/help/ and /students/help/). Head 5de2b28 (commits e27fe7b feature, f8dde0c test fix, 5de2b28 docs); both PR head check runs (139924297892 and 139706251415) independently retrieved completed/success, no passing count, and the PR was mergeable/clean at merge. The second run started before the PR was opened and which commit it tested was not checked. The first owner-supplied CI log (424 tests, one failure) is preserved in TICKETS.md. Merge-commit CI not independently verified.

PR #13 merged at 71b3d06: documentation only, recording the NAV-02 merge. Head 98876f2 check runs 139539724737 and 139540299962 independently successful, no passing count; merge-commit CI not independently verified.

PR #12 merged at c1d0042: NAV-02 orange underline on section headings (h2 and h3) in templates/base.html, plus docs. Head b41a8bf check runs 139533203220 and 139534192102 independently successful, no passing count. Owner reports CI passed after the merge; the merge-commit run was not independently retrieved.

PR #11 merged at 36152f9: NAV-01 home page with Owner, Instructor and Student sign-in cards, Home and My workspace tabs and a colorful framed layout. Head 882c8e3 check runs 139525500905 and 139525795466 independently successful, no passing count; merge-commit CI not independently verified. Owner reviewed it in a browser and reported that it looks good.

PR #8 merged at 03f332f: lesson and snapshot summary/instructions length checks (2000/20000, no truncation, no existing-data repair). Head runs 45091368598 and 45092648047 independently successful; post-merge CI not independently verified.

PR #9 merged at 70ce95d: local-only installation-wide MFA policy (MFA-POLICY01) with owner-page checkbox, audit records, migration accounts/0003_installation_mfa_policy and staff login/middleware enforcement. Head 83f2715 check run 139469414958 independently successful, no passing count; an earlier owner-supplied log with one failing test (a test-helper defect) is preserved in TICKETS.md. Owner reports migrate applied locally and the checkbox visible. Merge-commit CI not independently verified.

PR #10 merged at 08895cf: local-mode, MFA and LAN documentation only; head checks independently successful.

## Open acceptance
HELP-01: owner reads the owner, instructor and student manuals in a browser and checks each statement against the screens, in particular that instructors can create and enroll students, how invitations are activated, and the sign-in steps; checks the Help tab on staff, student, sign-in-adjacent and error pages, the current-tab marking, keyboard order and that the student manual shows no staff link.

NAV-01/NAV-02: browser check of contrast, tab wrapping on a narrow screen, keyboard order after the skip link, the Home and My workspace tabs on staff, student, sign-in and error pages, student pages showing no staff link, the notes shown when a sign-in is switched off, and the new heading underlines including inside the cards. Owner and Instructor share one staff login by design. Stem blue: needs a hex code or logo; the repository holds no brand color or logo file.

MFA-POLICY01: browser check that password-only sign-in works with the policy off for owners and instructors in every organization, that turning MFA back on forces verification again, that existing authenticators still work, that students never reach staff pages, and that the audit record appears. Defaults keep MFA required; production settings refuse to start when the local variables are set; never enable local mode with real data.

LAN-01: owner reports staff sign-in, student sign-in and lesson creation working from a second computer using DJANGO_ALLOWED_HOSTS and runserver 0.0.0.0:8000; the earlier failure was not diagnosed. Not implemented: a local-only trusted-origin or public-origin setting (invitation links keep a localhost address), HTTPS, hardened serving or a separate network zone for student routes. Plain HTTP on a development server is acceptable only on a trusted network.

Branches: feature/home-navigation, feature/orange-heading-underlines, docs/nav-02-merge-status, docs/local-mode-mfa-lan, feature/local-mfa-policy and feature/help-manuals still exist and none was deleted; docs/help-manuals-merge-status is open. The available GitHub connector has no branch-delete tool, so deletion is a manual step in the GitHub interface.

## Carry-forward
Skip-link PR7 merged at ff2f68c, guarded319b980; pre-merge checks45085015833/45085254574 independently successful. Owner reported merge CI passed at19:24 EST (run/testedSHA/runtime/count unknown). Actual focus/next-Tab/outline/no-JavaScript/cross-browser acceptance remains open. BUG003 REVIEW for onboarding browser and token-path logging. ASSIGN01/02/ROSTER-ASSIGN01 IN_PROGRESS for browser A/B/stale/identity-switch/back/reset/expiry/revocation/roster acceptance. Prior assignment/progress/privacy browser results remain owner-reported.

Migrations: accounts 0003_installation_mfa_policy was applied locally per the owner's report. Lessons migration0003 assignment-progress application on the intended DB is still unverified; check status/plan and back up first, with no bootstrap rerun or inferred deployment. Progress history/reporting and durable review-token concurrency remain separate; no exactly-once guarantee. Preserve E08-05, branding/library/document/file safety/student delivery, audit/throttling/recovery/session/TLS/logging/privacy/retention/mail/deployment/backup/training gates. Python3.14 unverified; PDFs restricted.

All implementation/fix commits update action/tickets/status/affected guides/validation. Confirm each external write; feature branch/PR, guarded merges, preserve local changes/data/credentials and earlier failures. Prior detailed plan/evidence: https://github.com/pavanjains/lms/blob/ff2f68c1e67b6a24d3d8a6854f6187b3f89e49b6/ACTION_PLAN.md
