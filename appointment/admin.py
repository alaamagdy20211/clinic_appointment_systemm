from django.contrib import admin
from .models import Appointment, AppointmentRescheduleLog, ConsultationRecord

# Register your models here.
admin.site.register(Appointment)
admin.site.register(AppointmentRescheduleLog)
admin.site.register(ConsultationRecord)