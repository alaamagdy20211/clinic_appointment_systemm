from django import forms

class UpdateStatusForm(forms.Form):
    status = forms.ChoiceField(choices=[
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('COMPLETED', 'Completed'),
        ('NO_SHOW', 'No Show'),
        ('CANCELLED', 'Cancelled'),
    ])