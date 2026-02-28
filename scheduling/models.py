from django.db import models

class DoctorSchedule(models.Model):
    DAYS = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    
    doctor = models.ForeignKey('users.DoctorProfile', on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAYS) 
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    slot_duration = models.IntegerField(choices=[(15, '15 min'), (30, '30 min')], default=30)

    def __str__(self):
        return f"{self.doctor.user.username} - {self.get_day_of_week_display()}"

class ScheduleException(models.Model):
    doctor = models.ForeignKey('users.DoctorProfile', on_delete=models.CASCADE)
    date = models.DateField()
    reason = models.CharField(max_length=255)
    is_working_day = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.doctor.user.username} - {self.date}"

class AppointmentSlot(models.Model):
    doctor = models.ForeignKey('users.DoctorProfile', on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')

    def __str__(self):
        return f"{self.doctor.user.username} - {self.date} {self.start_time}"