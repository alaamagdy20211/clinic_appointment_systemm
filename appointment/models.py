from django.db import models, transaction, IntegrityError
from django.conf import settings
from scheduling.models import AppointmentSlot
from datetime import timedelta, datetime, time

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

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'slot'], 
                name='unique_doctor_slot'
            ),
        ]

    def __str__(self):
        return f"Appointment: {self.patient.username} with Dr. {self.doctor.username} on {self.slot.date} at {self.slot.start_time.strftime('%I:%M %p')}"

    def clean(self):

        buffer_td = timedelta(minutes=BUFFER_MINUTES)
        slot_start = datetime.combine(self.slot.date, self.slot.start_time) - buffer_td
        slot_end = datetime.combine(self.slot.date, self.slot.end_time) + buffer_td

        overlapping = Appointment.objects.filter(
            patient=self.patient_id,
            slot__date=self.slot.date,
            slot__start_time__lt=slot_end.time(),
            slot__end_time__gt=slot_start.time()
        ).exclude(pk=self.pk)
        if overlapping.exists():
            raise IntegrityError("This patient has an overlapping appointment.")

        if self.slot.is_booked:
            raise IntegrityError("This slot is already booked.")