from django import forms
from django.db import transaction
from .models import User, PatientProfile

class PatientRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    phone_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    @transaction.atomic
    def save(self, commit=True):

        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.PATIENT
        
        if commit:
            user.save() 
            patient_profile, created = PatientProfile.objects.get_or_create(user=user)
            patient_profile.phone_number = self.cleaned_data['phone_number']
            patient_profile.save()
            
        return user