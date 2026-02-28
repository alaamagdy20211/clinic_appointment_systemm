from django.db import models
from django.conf import settings
from scheduling.models import DoctorSchedule


class Appointment(models.Model):
    
    patient = models.ForeignKey(settings.AUTH_USER_MODEL , 
                                on_delete= models.CASCADE ,
                                related_name="patient_appointments",
                                limit_choices_to={'role': 'Patient'})
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL , 
                                on_delete= models.CASCADE ,
                                related_name="doctor_appointments",
                                limit_choices_to={'role': 'Doctor'})
    
    slot = models.ForeignKey( DoctorSchedule ,
                                on_delete= models.CASCADE ,
                                related_name="slot_appointments")
    

    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta :
         constraints = [
        ] 
         ordering = ['-created_at']



# Create your models here.
