from django import forms
from .models import Appointment

class UpdateStatusForm(forms.Form):
    status = forms.ChoiceField(choices=[
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('COMPLETED', 'Completed'),
        ('NO_SHOW', 'No Show'),
        ('CANCELLED', 'Cancelled'),
    ],widget=forms.Select(attrs={'class': 'form-control'}))

    reason = forms.CharField(widget=forms.Textarea, required=False)


    def clean(self):
        cleaned_data=super().clean()
        status=cleaned_data.get("status")
        reason=cleaned_data.get("reason")

        if status in ['CANCELLED', 'NO_SHOW','COMPLETED'] and not reason:
            raise forms.ValidationError("you must provide a reason")

        return cleaned_data