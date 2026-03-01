from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages

class RoleRequiredMixin(AccessMixin):
    """Base mixin to strictly enforce role-based access."""
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        if request.user.role not in self.allowed_roles:
            messages.error(request, "You do not have permission to view this page.")
            return redirect('home')
            
        return super().dispatch(request, *args, **kwargs)


class PatientRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['PATIENT']

class DoctorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['DOCTOR']

class ReceptionistRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['RECEPTIONIST']

class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN']

class StaffRequiredMixin(RoleRequiredMixin):
    """For views that Doctors, Receptionists, and Admins can all access, but Patients cannot."""
    allowed_roles = ['DOCTOR', 'RECEPTIONIST', 'ADMIN']

class PatientOrDoctorRequiredMixin(RoleRequiredMixin):
    """For views that both Patients and Doctors can access, but Receptionists and Admins cannot."""
    allowed_roles = ['PATIENT', 'DOCTOR']