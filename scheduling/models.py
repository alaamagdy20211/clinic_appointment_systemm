from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class DoctorSchedule(models.Model):
    DAYS = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_appointment",
        limit_choices_to={'role': 'DOCTOR'}
    )
    day_of_week = models.IntegerField(choices=DAYS) 
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    slot_duration = models.IntegerField(choices=[(15, '15 min'), (30, '30 min')], default=30)

    def __str__(self):
        return f"{self.doctor.username} - {self.get_day_of_week_display()}"
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

class ScheduleException(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_appointmen",
        limit_choices_to={'role': 'DOCTOR'}
    )
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)    
    end_time = models.TimeField(null=True, blank=True)
    slot_duration = models.IntegerField(choices=[(15, '15 min'), (30, '30 min')], default=30)
    reason = models.CharField(max_length=255)
    is_working_day = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.doctor.username} - {self.date}"

    def clean(self):
        start_time = self.start_time
        end_time = self.end_time
        slot_duration = self.slot_duration
        if self.is_working_day:
            if start_time and end_time:
                if start_time >= end_time:
                    raise ValidationError("Start time must be before end time.")

                if slot_duration and (end_time.hour * 60 + end_time.minute) - (start_time.hour * 60 + start_time.minute) < slot_duration:
                    raise ValidationError("The time range must be at least as long as the slot duration.")
                
            else:
                raise ValidationError("Working day exceptions must have start and end times defined.")





class AppointmentSlot(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_appointme",
        limit_choices_to={'role': 'DOCTOR'}
    )    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'date', 'start_time') #  to ensure the uniqueness of each slot 
        

    def __str__(self):
             return f"{self.date} | {self.start_time.strftime('%I:%M %p')}"

    # def clean(self):
        

# def validate_time_range():
#     if start_time >= end_time:
#         raise ValidationError("Start time must be before end time.")