from django import forms

from apps.classrooms.forms import ConfirmationForm
from apps.lessons.models import GRADE_CHOICES, LESSON_FIELDS, Lesson


class LessonForm(forms.ModelForm):
    confirm = forms.BooleanField(label="I confirm this lesson change.")
    expected_version = forms.IntegerField(min_value=1, required=False, widget=forms.HiddenInput)

    class Meta:
        model = Lesson
        fields = list(LESSON_FIELDS)
        help_texts = {"lego_url": "HTTPS education.lego.com links only; availability is not checked."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["expected_version"].required = True
            self.initial["expected_version"] = self.instance.version


class ArchiveForm(ConfirmationForm):
    expected_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)


class FilterForm(forms.Form):
    q = forms.CharField(max_length=100, required=False, label="Search title or summary")
    kit = forms.ChoiceField(choices=[("", "All kits"), *Lesson.Kit.choices], required=False)
    grade = forms.TypedChoiceField(choices=[("", "All grades"), *GRADE_CHOICES],
                                   coerce=int, empty_value=None, required=False)
    status = forms.ChoiceField(choices=[("active", "Active"), ("archived", "Archived"),
                                        ("all", "All visible")], required=False)
