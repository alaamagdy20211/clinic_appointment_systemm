from django import forms
from django.db import transaction
from .models import User, PatientProfile

class PatientRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    phone_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
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
    
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

class PatientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['phone_number']


from .models import DoctorProfile, ReceptionistProfile

class DoctorRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    specialization = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.Role.DOCTOR
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                phone_number=self.cleaned_data['phone_number'],
            )
        return user


class ReceptionistRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    phone_number = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.Role.RECEPTIONIST
        if commit:
            user.save()
            ReceptionistProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
            )
        return user