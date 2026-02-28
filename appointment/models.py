from django.db import models,transaction
from django.conf import settings
from scheduling.models import DoctorSchedule
from django.core.exceptions import ValidationError
from django.utils import timezone


class Appointment(models.Model):
    
    patient = models.ForeignKey(settings.AUTH_USER_MODEL , 
                                on_delete= models.CASCADE ,
                                related_name="patient_appointments",
                                limit_choices_to={'role': 'PATIENT'})
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL ,
                                on_delete= models.CASCADE ,
                                related_name="doctor_appointments",
                                limit_choices_to={'role': 'DOCTOR'})
    
    slot = models.ForeignKey( DoctorSchedule ,
                                on_delete= models.CASCADE ,
                                related_name="slot_appointments")
    

    created_at = models.DateTimeField(auto_now_add=True)
    check_in_time = models.DateTimeField(null=True, blank=True)

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CHECKED_IN = "CHECKED_IN", "Checked In"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No Show"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED
    )

    def __str__(self):
        return f"Appointment {self.id} - {self.status}"


    class Meta :
         constraints = [ models.UniqueConstraint(
                fields=['slot'],
                name='unique_slot_booking'
            )
        ]
         ordering = ['-created_at']

# Create your models here.

    @transaction.atomic
    def confirm (self,user):
        if self.status != self.Status.REQUESTED:
            raise ValidationError("Only requested appointments can be confirmed.")
        if user.role not in ['Doctor', 'Receptionist']:
            raise ValidationError("Only Doctor or Receptionist can confirm appointments.")


        self.status = self.Status.CONFIRMED
        self.save()

    @transaction.atomic
    def cancel(self,user):
        if self.status not in [self.Status.REQUESTED, self.Status.CONFIRMED]:
            raise ValidationError("Only requested appointments can be cancelled.")

        if user.role  != 'Patient' and user != self.patient:
            raise ValidationError("Only Patient can cancel his own appointments.")

        self.status = self.Status.CANCELLED
        self.save()

    @transaction.atomic
    def check_in(self,user):
        if self.status != self.Status.CONFIRMED:
            raise ValidationError("Only confirmed appointments can be checked in.")

        if user.role not in ['Doctor', 'Receptionist']:
            raise ValidationError("Only Doctor or Receptionist can check_in appointments.")

        self.status = self.Status.CHECKED_IN
        self.check_in_time = timezone.now()
        self.save()


    def mark_no_show(self,user):
        if self.status != self.Status.CONFIRMED:
            raise ValidationError("Only confirmed appointments can be marked no show.")

        if user.role not in ['Doctor', 'Receptionist']:
            raise ValidationError("Only Doctor or Receptionist can mark no-show appointments.")

        self.status = self.Status.NO_SHOW
        self.save()


    def complete(self,user):
        if self.status != self.Status.CHECKED_IN:
            raise ValidationError("Only checked in-appointments can be completed.")
        if user.role !='Doctor':
            raise ValidationError("Only Doctor can complete appointments.")

        # check in heba part about consultation record lma t3mlo fi model bt3aha howa mawgod wla laa
        # if not hasattr(self, 'consultationrecord'):
        #     raise ValidationError("Consultation record must be completed first.")

        self.status = self.Status.COMPLETED
        self.save()