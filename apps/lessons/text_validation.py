from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator


def validate_lesson_text(instance):
    """Check text bounds after normal model cleaning, without changing content."""
    errors = {}
    for name in ("summary", "instructions"):
        limit = instance._meta.get_field(name).max_length
        try:
            MaxLengthValidator(limit)(getattr(instance, name))
        except ValidationError as error:
            errors[name] = error
    if errors:
        raise ValidationError(errors)
