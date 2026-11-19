from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase, override_settings

from apps.accounts.models import StudentProfile
from apps.classrooms.models import ClassEnrollment, ClassInstructor, Classroom
from apps.classrooms.policies import visible_classrooms, visible_class_students, visible_students
from apps.classrooms.services import (
    archive_classroom, assign_instructor, create_classroom, end_enrollment,
    enroll_student, remove_instructor,
)
from apps.organizations.models import Organization


@override_settings(LMS_STAFF_AUTH_ENABLED=True)
class ClassroomAccessTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic center")
        self.other = Organization.objects.create(name="Other center")
        self.owner = self.user("owner", "OWNER")
        self.teacher = self.user("teacher", "INSTRUCTOR")
        self.second = self.user("second", "INSTRUCTOR")
        self.student = self.user("student", "STUDENT")
        self.hidden = self.user("hidden", "STUDENT")
        self.foreign_owner = self.user("foreignowner", "OWNER", self.other)
        self.foreign_student = self.user("foreignstudent", "STUDENT", self.other)
        self.room = create_classroom(actor=self.owner, name="Robotics")
        self.extra = create_classroom(actor=self.owner, name="Prime")
        self.foreign = create_classroom(actor=self.foreign_owner, name="Robotics")
        assign_instructor(actor=self.owner, classroom_id=self.room.pk, instructor_id=self.teacher.pk)
        enroll_student(actor=self.owner, classroom_id=self.room.pk, student_id=self.student.pk)

    def user(self, name, role, org=None):
        user = get_user_model().objects.create_user(
            username=name, email=name + "@example.test" if role != "STUDENT" else "",
            role=role, organization=org or self.org,
        )
        user.is_verified = lambda: True
        if role == "STUDENT":
            StudentProfile.objects.create(user=user, grade="4")
        return user

    def test_owner_scope_and_instructor_scope(self):
        self.assertSetEqual(set(visible_classrooms(self.owner)), {self.room, self.extra})
        self.assertSetEqual(set(visible_classrooms(self.teacher)), {self.room})
        self.assertFalse(visible_classrooms(self.second).exists())
        self.assertSetEqual(set(visible_students(self.teacher)), {self.student})
        self.assertSetEqual(set(visible_students(self.owner)), {self.student, self.hidden})

    def test_shared_student_does_not_grant_other_class(self):
        enroll_student(actor=self.owner, classroom_id=self.extra.pk, student_id=self.student.pk)
        assign_instructor(actor=self.owner, classroom_id=self.extra.pk, instructor_id=self.second.pk)
        self.assertSetEqual(set(visible_students(self.second)), {self.student})
        with self.assertRaises(PermissionDenied):
            visible_class_students(self.teacher, self.extra.pk)
        self.assertSetEqual(set(visible_class_students(self.teacher, self.room.pk)), {self.student})

    def test_instructor_cannot_create_archive_or_change_staff(self):
        actions = [
            lambda: create_classroom(actor=self.teacher, name="Denied"),
            lambda: archive_classroom(actor=self.teacher, classroom_id=self.room.pk),
            lambda: assign_instructor(actor=self.teacher, classroom_id=self.room.pk, instructor_id=self.second.pk),
            lambda: remove_instructor(actor=self.teacher, classroom_id=self.room.pk, instructor_id=self.teacher.pk),
        ]
        for action in actions:
            with self.subTest(action=action), self.assertRaises(PermissionDenied):
                action()

    def test_enrollment_requires_class_and_student_access(self):
        with self.assertRaises(PermissionDenied):
            enroll_student(actor=self.teacher, classroom_id=self.room.pk, student_id=self.hidden.pk)
        with self.assertRaises(PermissionDenied):
            enroll_student(actor=self.second, classroom_id=self.room.pk, student_id=self.student.pk)
        assign_instructor(actor=self.owner, classroom_id=self.extra.pk, instructor_id=self.teacher.pk)
        link = enroll_student(actor=self.teacher, classroom_id=self.extra.pk, student_id=self.student.pk)
        self.assertTrue(link.is_active)

    def test_repeat_remove_and_readd_reuse_links(self):
        for _ in range(2):
            assign_instructor(actor=self.owner, classroom_id=self.room.pk, instructor_id=self.teacher.pk)
            enroll_student(actor=self.owner, classroom_id=self.room.pk, student_id=self.student.pk)
        original = ClassInstructor.objects.get(classroom=self.room, instructor=self.teacher).pk
        for _ in range(2):
            remove_instructor(actor=self.owner, classroom_id=self.room.pk, instructor_id=self.teacher.pk)
        renewed = assign_instructor(actor=self.owner, classroom_id=self.room.pk, instructor_id=self.teacher.pk)
        self.assertEqual(renewed.pk, original)
        for _ in range(2):
            end_enrollment(actor=self.teacher, classroom_id=self.room.pk, student_id=self.student.pk)
        enroll_student(actor=self.owner, classroom_id=self.room.pk, student_id=self.student.pk)
        self.assertEqual(ClassEnrollment.objects.count(), 1)

    def test_removed_membership_removes_visibility_and_write_access(self):
        remove_instructor(actor=self.owner, classroom_id=self.room.pk, instructor_id=self.teacher.pk)
        self.assertFalse(visible_students(self.teacher).exists())
        with self.assertRaises(PermissionDenied):
            end_enrollment(actor=self.teacher, classroom_id=self.room.pk, student_id=self.student.pk)

    def test_foreign_ids_rejected(self):
        with self.assertRaises(PermissionDenied):
            archive_classroom(actor=self.owner, classroom_id=self.foreign.pk)
        with self.assertRaises(PermissionDenied):
            enroll_student(actor=self.owner, classroom_id=self.room.pk, student_id=self.foreign_student.pk)
        with self.assertRaises(PermissionDenied):
            assign_instructor(actor=self.owner, classroom_id=self.room.pk, instructor_id=self.foreign_owner.pk)

    def test_wrong_role_and_missing_profile_rejected(self):
        with self.assertRaises(PermissionDenied):
            assign_instructor(actor=self.owner, classroom_id=self.room.pk, instructor_id=self.student.pk)
        StudentProfile.objects.filter(user=self.hidden).delete()
        with self.assertRaises(ValidationError):
            enroll_student(actor=self.owner, classroom_id=self.room.pk, student_id=self.hidden.pk)
        self.assertFalse(ClassEnrollment.objects.filter(student=self.hidden).exists())

    def test_archive_retains_links_and_blocks_instructor(self):
        for _ in range(2):
            archive_classroom(actor=self.owner, classroom_id=self.room.pk)
        self.assertTrue(ClassEnrollment.objects.filter(classroom=self.room).exists())
        self.assertFalse(visible_classrooms(self.teacher).exists())
        self.assertTrue(visible_classrooms(self.owner).filter(pk=self.room.pk).exists())
        with self.assertRaises(PermissionDenied):
            enroll_student(actor=self.owner, classroom_id=self.room.pk, student_id=self.hidden.pk)

    def test_stale_deactivated_actor_rejected(self):
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            create_classroom(actor=self.owner, name="Denied")
        with self.assertRaises(PermissionDenied):
            visible_classrooms(self.owner)

    def test_stale_demoted_actor_cannot_create(self):
        get_user_model().objects.filter(pk=self.owner.pk).update(role="INSTRUCTOR")
        with self.assertRaises(PermissionDenied):
            create_classroom(actor=self.owner, name="Denied")

    def test_mfa_anonymous_and_student_denied(self):
        self.owner.is_verified = lambda: False
        for actor in (self.owner, AnonymousUser(), self.student):
            with self.subTest(actor=actor), self.assertRaises(PermissionDenied):
                visible_students(actor)

    @override_settings(LMS_STAFF_AUTH_ENABLED=False)
    def test_disabled_gate(self):
        with self.assertRaises(PermissionDenied):
            visible_classrooms(self.owner)
        with self.assertRaises(PermissionDenied):
            create_classroom(actor=self.owner, name="Denied")

    def test_inactive_org_and_target_denied(self):
        get_user_model().objects.filter(pk=self.hidden.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            enroll_student(actor=self.owner, classroom_id=self.room.pk, student_id=self.hidden.pk)
        Organization.objects.filter(pk=self.org.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            visible_classrooms(self.owner)

    def test_failed_write_rolls_back(self):
        with patch("apps.classrooms.services.ClassEnrollment.save", side_effect=RuntimeError("synthetic")):
            with self.assertRaises(RuntimeError):
                enroll_student(actor=self.owner, classroom_id=self.extra.pk, student_id=self.hidden.pk)
        self.assertFalse(ClassEnrollment.objects.filter(classroom=self.extra).exists())

    def test_invalid_duplicate_class_leaves_no_extra_record(self):
        with self.assertRaises(ValidationError):
            create_classroom(actor=self.owner, name=" ROBOTICS ")
        self.assertEqual(Classroom.objects.filter(organization=self.org).count(), 2)
