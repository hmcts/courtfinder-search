from django import forms
from django.core.exceptions import ValidationError


def require_no_value(value):
    if value:
        raise ValidationError("Field must be empty")


class FeedbackForm(forms.Form):
    feedback_text = forms.CharField(label='feedback_text', max_length=200)
    feedback_referer = forms.CharField(label='feedback_referer', max_length=512)
    feedback_email = forms.CharField(
        label='feedback_email', max_length=2000, required=False)

    # honeypot field - will be hidden in css
    feedback_name = forms.CharField(label="Your name", required=False, validators=[require_no_value])
