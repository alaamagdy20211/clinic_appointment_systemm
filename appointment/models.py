from django.db import models, transaction, IntegrityError
from django.conf import settings
from scheduling.models import AppointmentSlot,DoctorSchedule
from datetime import timedelta, datetime, time
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

BUFFER_MINUTES = 5  


class Appointment(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
        limit_choices_to={'role': 'PATIENT'}
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_appointments",
        limit_choices_to={'role': 'DOCTOR'}
    )
    slot = models.ForeignKey(
        AppointmentSlot,
        on_delete=models.CASCADE,
        related_name="slot_appointments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    check_in_time = models.DateTimeField(null=True, blank=True)


    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'slot'],
                condition=Q(status__in=['REQUESTED', 'CONFIRMED', 'CHECKED_IN','COMPLETED']),
                name='unique_doctor_slot'
            ),
        ]

    def __str__(self):
        return f"Appointment: {self.patient.username} with Dr. {self.doctor.username} on {self.slot.date} at {self.slot.start_time.strftime('%I:%M %p')  }-{self.status}"

    def clean(self):
        active_statuses = [
            self.Status.REQUESTED,
            self.Status.CONFIRMED,
            self.Status.CHECKED_IN,
            self.Status.COMPLETED
        ]

        buffer_td = timedelta(minutes=BUFFER_MINUTES)
        slot_start = datetime.combine(self.slot.date, self.slot.start_time) - buffer_td
        slot_end = datetime.combine(self.slot.date, self.slot.end_time) + buffer_td

        overlapping = Appointment.objects.filter(
            patient=self.patient_id,
            slot__date=self.slot.date,
            slot__start_time__lt=slot_end.time(),
            slot__end_time__gt=slot_start.time(),
            status__in=active_statuses
        ).exclude(pk=self.pk)
        if overlapping.exists():
            raise IntegrityError("This patient has an overlapping appointment.")

        if self.slot.is_booked:
            raise IntegrityError("This slot is already booked.")
        


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

    # def __str__(self):
    #     return f"Appointment {self.id} - {self.status}"


  

# Create your models here.

    @transaction.atomic
    def confirm (self,user):
        if self.status != self.Status.REQUESTED:
            raise ValidationError("Only requested appointments can be confirmed.")
        if user.role not in ['DOCTOR', 'RECEPTIONIST']:
            raise ValidationError("Only Doctor or Receptionist can confirm appointments.")


        self.status = self.Status.CONFIRMED
        self.save()

    @transaction.atomic
    def cancel(self,user):
        if self.status not in [self.Status.REQUESTED, self.Status.CONFIRMED]:
            raise ValidationError("Only requested appointments can be cancelled.")

        if user.role  != 'PATIENT' and user != self.patient:
            raise ValidationError("Only Patient can cancel his own appointments.")

        self.status = self.Status.CANCELLED
        self.save()
        self.slot.is_booked = False
        self.slot.save()


    @transaction.atomic
    def check_in(self,user):
        if self.status != self.Status.CONFIRMED:
            raise ValidationError("Only confirmed appointments can be checked in.")

        if user.role not in ['DOCTOR', 'RECEPTIONIST']:
            raise ValidationError("Only Doctor or Receptionist can check_in appointments.")

        self.status = self.Status.CHECKED_IN
        self.check_in_time = timezone.now()
        self.save()


    def mark_no_show(self,user):
        if self.status != self.Status.CONFIRMED:
            raise ValidationError("Only confirmed appointments can be marked no show.")

        if user.role not in  ['DOCTOR', 'RECEPTIONIST']:
            raise ValidationError("Only Doctor or Receptionist can mark no-show appointments.")

        self.status = self.Status.NO_SHOW
        self.save()
        self.slot.is_booked = False
        self.slot.save()


    def complete(self,user):
        if self.status != self.Status.CHECKED_IN:
            raise ValidationError("Only checked in-appointments can be completed.")
        if user.role !='DOCTOR':
            raise ValidationError("Only Doctor can complete appointments.")

        # check in heba part about consultation record lma t3mlo fi model bt3aha howa mawgod wla laa
        # if not hasattr(self, 'consultationrecord'):
        #     raise ValidationError("Consultation record must be completed first.")

        self.status = self.Status.COMPLETED
        self.save()