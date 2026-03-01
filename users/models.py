from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        DOCTOR = 'DOCTOR', 'Doctor'
        PATIENT = 'PATIENT', 'Patient'
        RECEPTIONIST = 'RECEPTIONIST', 'Receptionist'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)

    def save(self, *args, **kwargs):
        if not self.pk and self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.specialization}"
    
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username
    
class ReceptionistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='receptionist_profile')
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username