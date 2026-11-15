from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from apps.accounts.models import StudentProfile
from apps.classrooms.models import ClassEnrollment, ClassInstructor, Classroom
from apps.organizations.models import Organization


class ClassroomModelTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Synthetic center")
        self.other = Organization.objects.create(name="Other center")
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner", email="owner@example.test",
                                              role="OWNER", organization=self.org)
        self.teacher = User.objects.create_user(username="teacher", email="teacher@example.test",
                                                role="INSTRUCTOR", organization=self.org)
        self.student = User.objects.create_user(username="student", role="STUDENT", organization=self.org)
        StudentProfile.objects.create(user=self.student, grade="4")
        self.room = self.save_valid(Classroom(organization=self.org, name="Robotics", created_by=self.owner))

    def save_valid(self, obj):
        obj.full_clean()
        obj.save()
        return obj

    def test_name_trim_and_blank_validation(self):
        room = self.save_valid(Classroom(organization=self.org, name="  Prime  ", created_by=self.owner))
        self.assertEqual(room.name, "Prime")
        with self.assertRaises(ValidationError):
            Classroom(organization=self.org, name="   ", created_by=self.owner).full_clean()

    def test_class_name_unique_within_org_at_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Classroom.objects.create(organization=self.org, name=" ROBOTICS ", created_by=self.owner)

    def test_same_name_allowed_in_other_org(self):
        owner = get_user_model().objects.create_user(username="otherowner", email="other@example.test",
                                                     role="OWNER", organization=self.other)
        self.save_valid(Classroom(organization=self.other, name="Robotics", created_by=owner))

    def test_creator_must_be_staff_in_same_org(self):
        for creator, org in ((self.student, self.org), (self.owner, self.other)):
            with self.subTest(creator=creator.pk, org=org.pk), self.assertRaises(ValidationError):
                Classroom(organization=org, name="Invalid", created_by=creator).full_clean()

    def test_shared_instructors_and_student_across_classes(self):
        second = self.save_valid(Classroom(organization=self.org, name="Second", created_by=self.owner))
        teacher2 = get_user_model().objects.create_user(username="teacher2", email="teacher2@example.test",
                                                       role="INSTRUCTOR", organization=self.org)
        for teacher in (self.teacher, teacher2):
            self.save_valid(ClassInstructor(classroom=self.room, instructor=teacher))
        for room in (self.room, second):
            self.save_valid(ClassEnrollment(classroom=room, student=self.student))
        self.assertEqual(self.room.instructor_links.count(), 2)
        self.assertEqual(self.student.classroom_enrollments.count(), 2)

    def test_duplicate_memberships_rejected_by_database(self):
        for model, values in (
            (ClassInstructor, {"classroom": self.room, "instructor": self.teacher}),
            (ClassEnrollment, {"classroom": self.room, "student": self.student}),
        ):
            self.save_valid(model(**values))
            with self.subTest(model=model.__name__), self.assertRaises(IntegrityError), transaction.atomic():
                model.objects.create(**values)

    def test_wrong_roles_rejected(self):
        for link in (ClassInstructor(classroom=self.room, instructor=self.owner),
                     ClassEnrollment(classroom=self.room, student=self.teacher)):
            with self.subTest(model=type(link).__name__), self.assertRaises(ValidationError):
                link.full_clean()

    def test_cross_org_links_rejected(self):
        get_user_model().objects.filter(pk__in=[self.teacher.pk, self.student.pk]).update(organization=self.other)
        for link in (ClassInstructor(classroom=self.room, instructor=self.teacher),
                     ClassEnrollment(classroom=self.room, student=self.student)):
            with self.subTest(model=type(link).__name__), self.assertRaises(ValidationError):
                link.full_clean()

    def test_student_profile_required(self):
        StudentProfile.objects.filter(user=self.student).delete()
        with self.assertRaises(ValidationError):
            ClassEnrollment(classroom=self.room, student=self.student).full_clean()

    def test_inactive_account_class_and_org_rejected_for_active_links(self):
        get_user_model().objects.filter(pk=self.teacher.pk).update(is_active=False)
        with self.assertRaises(ValidationError):
            ClassInstructor(classroom=self.room, instructor=self.teacher).full_clean()
        Classroom.objects.filter(pk=self.room.pk).update(is_active=False)
        with self.assertRaises(ValidationError):
            ClassEnrollment(classroom=self.room, student=self.student).full_clean()
        Classroom.objects.filter(pk=self.room.pk).update(is_active=True)
        Organization.objects.filter(pk=self.org.pk).update(is_active=False)
        with self.assertRaises(ValidationError):
            ClassEnrollment(classroom=self.room, student=self.student).full_clean()

    def test_inactive_membership_can_be_retained_after_deactivation(self):
        link = self.save_valid(ClassInstructor(classroom=self.room, instructor=self.teacher))
        get_user_model().objects.filter(pk=self.teacher.pk).update(is_active=False)
        link.is_active = False
        self.save_valid(link)
        self.assertEqual(ClassInstructor.objects.count(), 1)

    def test_archiving_preserves_links_and_protects_deletion(self):
        self.save_valid(ClassEnrollment(classroom=self.room, student=self.student))
        self.room.is_active = False
        self.save_valid(self.room)
        self.assertEqual(self.room.enrollment_links.count(), 1)
        with self.assertRaises(ProtectedError):
            self.room.delete()
