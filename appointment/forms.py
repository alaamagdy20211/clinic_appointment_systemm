from django import forms
from .models import Appointment
from scheduling.models import AppointmentSlot
from users.models import User
from datetime import datetime

class DoctorSelectionForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(role='DOCTOR'),
        empty_label="Select Doctor"
    )
    slot = forms.ModelChoiceField(
        queryset=AppointmentSlot.objects.none(),
        empty_label="Select Slot"
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'slot']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'doctor' in self.data:
            try:
                doctor_id = int(self.data.get('doctor'))
                self.fields['slot'].queryset = AppointmentSlot.objects.filter(
                    doctor_id=doctor_id,
                    is_booked=False,
                    date__gte=datetime.now().date()
                ).order_by('date', 'start_time')
            except (ValueError, TypeError):
                self.fields['slot'].queryset = AppointmentSlot.objects.none()