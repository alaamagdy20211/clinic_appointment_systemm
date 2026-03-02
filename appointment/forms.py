from django import forms
from .models import Appointment
from users.models import User
from scheduling.models import AppointmentSlot
from datetime import timedelta, datetime , timezone
from django import forms
from .models import Appointment, AppointmentSlot

class UpdateStatusForm(forms.Form):
    status = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}))
    # reason = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # get the logged-in user
        super().__init__(*args, **kwargs)

        # Define role-based choices
        if user.role == "PATIENT":
            self.fields['status'].choices = [
                ('CANCELLED', 'Cancelled'),
            ]
        elif user.role == "DOCTOR":
            self.fields['status'].choices = [
                ('CONFIRMED', 'Confirmed'),
                ('CHECKED_IN', 'Checked In'),
                ('NO_SHOW', 'No Show'),
                ('COMPLETED', 'Completed'),
            ]
        elif user.role == "RECEPTIONIST":
            self.fields['status'].choices = [
                ('CONFIRMED', 'Confirmed'),
                ('CHECKED_IN', 'Checked In'),
                ('NO_SHOW', 'No Show'),
            ]
        elif user.role == "ADMIN":
            self.fields['status'].choices = [
                ('CONFIRMED', 'Confirmed'),
                ('CHECKED_IN', 'Checked In'),
                ('NO_SHOW', 'No Show'),
                ('CANCELLED', 'Cancelled'),
                ('COMPLETED', 'Completed'),
            ]


    def clean(self):
        cleaned_data=super().clean()
        status=cleaned_data.get("status")
        return cleaned_data


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
                    # date__gte=timezone.now().date()
                ).order_by('date', 'start_time')
            except (ValueError, TypeError):
                self.fields['slot'].queryset = AppointmentSlot.objects.none()




class RescheduleAppointmentForm(forms.Form):
    new_slot = forms.ModelChoiceField(queryset=AppointmentSlot.objects.none())
    reason = forms.CharField(widget=forms.Textarea, max_length=500)

    def __init__(self, *args, **kwargs):
        appointment = kwargs.pop('appointment', None)
        super().__init__(*args, **kwargs)
        if appointment:

            self.fields['new_slot'].queryset = AppointmentSlot.objects.filter(
                doctor=appointment.doctor,
                is_booked=False,
                # date__gte=timezone.now().date()
            ).order_by('date', 'start_time')