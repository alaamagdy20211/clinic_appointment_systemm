from django import forms
from .models import DoctorSchedule, ScheduleException

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

class ScheduleExceptionForm(forms.ModelForm):
    class Meta:
        model = ScheduleException
        fields = ['date', 'reason', 'is_working_day']
        # widgets = {
        #     'date': forms.DateInput(format='%Y-%m-%d'),
        #     'reason': forms.TextInput(),
        #     'is_working_day': forms.CheckboxInput(),
        # }