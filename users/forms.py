from django import forms
from django.db import transaction
from .models import User, PatientProfile
import re
from .models import DoctorProfile, ReceptionistProfile


class PatientRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    phone_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

        # def clean_phone_number(self):
        #     phone_number = self.cleaned_data.get('phone_number')
        #     if not phone_number:
        #         raise forms.ValidationError("Phone number is required for patients.")
        #     if len(phone_number) != 11 or not phone_number.isdigit():
        #         raise forms.ValidationError("Phone number must be 11 digits.")
        #     if not phone_number.startswith('01'):
        #         raise forms.ValidationError("Phone number must start with '01'.")
        #     return phone_number
        
        def clean_password(self):
            password = self.cleaned_data.get('password')
            if len(password) < 8 or password.isdigit() or password.isalpha():
                raise forms.ValidationError("Password must be at least 8 characters long and contain both letters and numbers.")
            return password
        
        def clean_email(self):
            email = self.cleaned_data.get('email')
            if not email:
                raise forms.ValidationError("Email is required.")
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("A user with this email already exists.")
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(email_pattern, email):
                raise forms.ValidationError("Enter a valid email address.")
            return email
        
        def clean_username(self):
            username = self.cleaned_data.get('username')
            if not username:
                raise forms.ValidationError("Username is required.")
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("A user with this username already exists.")
            return username
        
        def clean_phone_number(self):
            phone_number = self.cleaned_data.get('phone_number')
            if not phone_number:
                raise forms.ValidationError("Phone number is required for patients.")
            if len(phone_number) != 11 or not phone_number.isdigit():
                raise forms.ValidationError("Phone number must be 11 digits.")
            if not phone_number.startswith('01'):
                raise forms.ValidationError("Phone number must start with '01'.")
            return phone_number
    
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
        fields = ['first_name', 'last_name', 'email']

class PatientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['phone_number']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise forms.ValidationError("Phone number is required for patients.")
        if len(phone_number) != 11 or not phone_number.isdigit():
            raise forms.ValidationError("Phone number must be 11 digits.")
        if not phone_number.startswith('01'):
            raise forms.ValidationError("Phone number must start with '01'.")
        return phone_number

    
    


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