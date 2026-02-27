from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PatientProfile, DoctorProfile, ReceptionistProfile

admin.site.register(User, UserAdmin)
admin.site.register(PatientProfile)
admin.site.register(DoctorProfile)
admin.site.register(ReceptionistProfile)