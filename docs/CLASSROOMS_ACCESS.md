# E08-02/E08-03 services and policies

Status REVIEW; authored tests and new CI pending. Extends E08-01; docs/CLASSROOMS.md describes schema boundaries. Its reference to services/policies as future work is historical and superseded here. No schema or route changes.

## Services
create_classroom, archive_classroom, assign_instructor, remove_instructor, enroll_student, end_enrollment use keyword arguments actor plus relevant IDs. Caller cannot choose organization/creator. Owner-only creation/archive and instructor changes. Assigned instructors may enroll already-visible students into active assigned classes and end enrollments there. Owners may clean up links in archived classes and enroll eligible same-organization students into active classes. No reactivation endpoint.

Every entry requires staff flag, authenticated actor and MFA proof from trusted request user; current active account, staff role and same active organization reloaded. Services lock organization then actor, class, target, link. This serializes cooperating services, not arbitrary raw ORM writes. full_clean enforces model role/organization/profile semantics; failures roll back. Existing inactive-account links can be removed. Absent removals return None, additions reactivate the same row, duplicate class names raise ValidationError. Malformed/nonexistent IDs must be translated to safe HTTP errors by future forms/views.

## Policies
visible_classrooms(actor), visible_students(actor), visible_class_students(actor, classroom_id). Unauthorized actors/rosters raise PermissionDenied. Owners see own organization's classes including archived; instructors only active memberships in active classes. Directory contains active students with profiles; instructors limited to active enrollment in visible classes. Archived class rosters unavailable through active roster policy. All querysets scoped to current organization; shared identity never grants another class. No lesson/feedback visibility is implied.

Read authorization checked on function call. Querysets are lazy; evaluate promptly per request and never cache/reuse as permission grants. Future views must select safe roster fields (ID/display name/grade), never serialize the complete User/password/MFA data. Write services always reauthorize. Database row-level security, triggers, audit and student-creator relationships not included. Existing role/organization editing must account for retained links before exposure.

## Verify
```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test apps.classrooms --settings=config.settings.ci
python manage.py test --settings=config.settings.ci
ruff check .
```

No migration needed beyond E08-01. Tests stub trusted MFA proof for service/policy units; actual browser MFA/CSRF coverage belongs to upcoming UI. PostgreSQL parallel mutation acceptance remains E08-05.
