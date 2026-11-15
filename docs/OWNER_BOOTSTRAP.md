# E04-02 — Initial owner bootstrap

## Scope
Creates the first organization and an active LMS OWNER account. It does not enable staff login, MFA, invitations, an admin route, or class access. The account is not a Django superuser and does not have framework is_staff privileges.

## Prerequisites
Apply migrations using the correct environment. Run this command only as an authorized deployment operator. Do not run concurrent bootstrap commands. This is an initial-installation tool, not account recovery or organization management.

## Interactive use (preferred)
```sh
python manage.py migrate
python manage.py bootstrap_owner --organization "Your Center" --username center-owner --email owner@example.com
```
The command prompts for and confirms a password without displaying it. Password validators are applied. Replace the example email with the real owner address before execution.

## Noninteractive use
Provide LMS_BOOTSTRAP_PASSWORD through an approved secret-injection mechanism and pass --noinput. Do not place an actual password in a command argument, Git, CI YAML, logs, or a committed environment file. Remove the environment variable after use. The command never prints the password.

```sh
# LMS_BOOTSTRAP_PASSWORD must already be securely injected.
python manage.py bootstrap_owner --organization "Your Center" --username center-owner --email owner@example.com --noinput
unset LMS_BOOTSTRAP_PASSWORD
```

## Repeat and failure behavior
- Exact repeat against one matching active organization and active owner is a no-op, even without the password variable.
- Existing accounts are never promoted, reactivated, renamed, or assigned a new password.
- Existing nonmatching organization data causes refusal; investigate instead of deleting records.
- Validation failures roll back newly created organization/account records.
- Concurrent conflicts return an error; inspect state before retrying.
- No success or error message should contain a password.

## Verification
```sh
python manage.py test apps.accounts.test_bootstrap --settings=config.settings.test
# With PostgreSQL environment exported:
DJANGO_SETTINGS_MODULE=config.settings.ci python manage.py test
python manage.py makemigrations --check --dry-run
```
Ten tests cover creation, no-op repeat, existing installation refusal, inactive owner refusal, missing password, password rejection, invalid email rollback, interactive confirmation, mismatch, and blank identifiers.

## Status
Authored and Python syntax checked only. Django/PostgreSQL tests and CI results are not verified in the authoring environment. No schema change is introduced. E04-02 remains awaiting runtime acceptance evidence. Do not claim staff access is usable until login, MFA, and authorization are implemented.
