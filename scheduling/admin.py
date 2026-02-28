from django.contrib import admin
from .models import DoctorSchedule, ScheduleException, AppointmentSlot
# Register your models here.


admin.site.register(DoctorSchedule)
admin.site.register(ScheduleException)
admin.site.register(AppointmentSlot)