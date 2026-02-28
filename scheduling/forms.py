from django import forms
from .models import DoctorSchedule

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = ['day_of_week', 'start_time', 'end_time', 'slot_duration']
        # widgets = {
        #     'day_of_week': forms.Select(choices=DoctorSchedule.DAYS),
        #     'start_time': forms.TimeInput(format='%H:%M'),
        #     'end_time': forms.TimeInput(format='%H:%M'),
        #     'slot_duration': forms.Select(choices=[(15, '15 min'), (30, '30 min')]),
        # }