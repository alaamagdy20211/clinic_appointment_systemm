from django.db import models,transaction
from django.views.generic import ListView,View
from .models import Appointment
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,get_object_or_404,redirect
from django.core.exceptions import ValidationError
from .forms import UpdateStatusForm


class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = "appointments/list.html"
    context_object_name = "appointments"

    def get_queryset(self):
        user = self.request.user
        print("Logged-in user:", user, user.role, user.username)  # <<-- add this

        if user.role == "PATIENT":
            return Appointment.objects.filter(patient=user)

        if user.role == "DOCTOR":
            return Appointment.objects.filter(doctor=user)

        return Appointment.objects.all()

class  UpdateAppointmentStatusView(View):
    template_name = "appointments/update_status.html"
    def get(self,request,pk):
        appointment=get_object_or_404(Appointment,pk=pk)
        form = UpdateStatusForm(initial={'status': appointment.status}, user=request.user)
        return render(request, self.template_name, {'form': form, 'appointment': appointment})

    def post(self,request,pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        form = UpdateStatusForm(request.POST,user=request.user)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            reason = form.cleaned_data.get('reason', '')
            try:

               with transaction.atomic():

                if new_status == 'CONFIRMED':
                    appointment.confirm(request.user)
                elif new_status == 'CANCELLED':
                    appointment.cancel(request.user)
                elif new_status == 'CHECKED_IN':
                    appointment.check_in(request.user)
                elif new_status == 'NO_SHOW':
                    appointment.mark_no_show(request.user)
                elif new_status == 'COMPLETED':
                    appointment.complete(request.user)
                else:
                    raise ValidationError("Invalid status.")

                messages.success(request, f"Appointment status updated to {new_status}.")
                return redirect("appointment_list")

            except ValidationError as e:
                form.add_error(None, e.message)


        return render(request, self.template_name, {'form': form, 'appointment': appointment})