from django.db import models
from django.conf import settings
from scheduling.models import AppointmentSlot

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

    def __str__(self):
            return (
        f"Appointment: {self.patient.username} "
        f"with Dr. {self.doctor.username} "
        f"on {self.slot.date} "
        f"at {self.slot.start_time.strftime('%I:%M %p')}"
    )