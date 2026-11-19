from django import forms

from apps.accounts.models import StudentProfile
from apps.classrooms.forms import ConfirmationForm


class StudentCreationForm(ConfirmationForm):
    username = forms.CharField(max_length=150, help_text="Choose a unique student username.")
    display_name = forms.CharField(max_length=100, label="Student display name")
    grade = forms.ChoiceField(choices=StudentProfile.Grade.choices)
    password1 = forms.CharField(max_length=128, strip=False, label="Student password",
                                widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    password2 = forms.CharField(max_length=128, strip=False, label="Confirm student password",
                                widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))

    def clean(self):
        data = super().clean()
        if data.get("password1") != data.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        return data
