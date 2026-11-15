# E08-01 classrooms foundation

Status REVIEW. Schema/model tests authored, not executed here. Migration and drift checks pending. No UI or authorization surface.

Classroom belongs to an organization and records name, description, active state, creator and timestamps. ClassInstructor and ClassEnrollment are unique class/account pairs with active state and timestamps. Multiple instructors and multiple class enrollments are supported. Existing accounts are reused. Database class-name uniqueness uses lower(trim(name)) per organization; clean strips surrounding whitespace and rejects blank names. Raw whitespace-only inserts are not fully prevented by the nonempty database check; validated services are mandatory before exposure.

Cross-table role/organization checks, active-link checks and student-profile checks run in full_clean, not automatically in save or bulk writes. These models do not authorize requests. No row-level security, triggers, transactional service layer, student-creator relationship, or audit log is introduced. Direct ORM writes remain privileged and can bypass semantic validation. Existing user role/organization changes must not be exposed without reviewing link consistency.

Creator must be staff in the class organization; owner-only creation will be enforced in E08-02. Historical creators need not stay active. Active links require an active account, organization and class. Inactive links can be retained for inactive accounts/classes; schema permits existing active links to remain when an account/class is deactivated. E08-03 must filter every access using current statuses. Archived classes do not delete links; reactivation workflow not included. PROTECT prevents accidental deletion of referenced classes/accounts/organizations; it is not a complete retention/audit policy.

No kit is forced at class level; Grade 4 kit choice belongs to later lesson/assignment behavior. No production capacity limit is hardcoded. Sharing student identity through one class must not expose records from another class.

## Verify after commit
With the normal local development environment loaded:

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --plan
python manage.py migrate
python manage.py test apps.classrooms --settings=config.settings.ci
python manage.py test --settings=config.settings.ci
ruff check .
```

Migration creates three new tables; no seed data or existing-account rewrite. Test settings only for tests, not browser server. Do not report passing results without actual output.

Next: E08-02 owner/assigned-instructor transactional services and E08-03 scoped read policies with MFA/current-actor checks, followed by UI and PostgreSQL race/browser acceptance.
