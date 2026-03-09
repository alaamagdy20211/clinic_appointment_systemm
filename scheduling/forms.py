from django import forms
from .models import DoctorSchedule, ScheduleException
from django.utils import timezone
from django.contrib.auth import get_user_model

INPUT_CLASS = "w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
SELECT_CLASS = "w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white"

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = ['day_of_week', 'start_time', 'end_time', 'slot_duration']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': SELECT_CLASS}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': INPUT_CLASS}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': INPUT_CLASS}),
            'slot_duration': forms.Select(attrs={'class': SELECT_CLASS}),
        }

class ScheduleExceptionForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(role="DOCTOR"),
        widget=forms.Select(attrs={'class': SELECT_CLASS}),
        required=True,
        label="Doctor"
    )

    class Meta:
        model = ScheduleException
        fields = ['doctor', 'date', 'reason', 'is_working_day', 'start_time', 'end_time', 'slot_duration']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASS}),
            'reason': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'is_working_day': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-400'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': INPUT_CLASS}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': INPUT_CLASS}),
            'slot_duration': forms.Select(attrs={'class': SELECT_CLASS}),
        }

    def clean_date(self):
        date = self.cleaned_data['date']
        if date and date < timezone.now().date():
            raise forms.ValidationError("Exception date cannot be in the past.")
        return date