from django import forms


class ConfirmationForm(forms.Form):
    confirm = forms.BooleanField(label="I confirm this change.")


class ClassroomForm(ConfirmationForm):
    name = forms.CharField(max_length=160)
    description = forms.CharField(required=False, widget=forms.Textarea, max_length=4000)


class TargetForm(ConfirmationForm):
    target = forms.TypedChoiceField(coerce=int, label="Account")

    def __init__(self, *args, choices, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target"].choices = [("", "Select an account"), *choices]
