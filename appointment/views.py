from django.views.generic import ListView
from .models import Appointment
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin



class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = "appointments/list.html"
    context_object_name = "appointments"

    def get_queryset(self):
        user = self.request.user

        if user.role == "PATIENT":
            return Appointment.objects.filter(patient=user)

        if user.role == "DOCTOR":
            return Appointment.objects.filter(doctor=user)

        return Appointment.objects.all()