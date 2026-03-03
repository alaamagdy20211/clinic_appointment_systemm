
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import transaction, IntegrityError
from django.utils.timezone import now
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required
from .forms import DoctorSelectionForm
from .models import Appointment, ConsultationRecord
from scheduling.models import AppointmentSlot
from django.db import models
from django.views.generic import ListView,View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,get_object_or_404,redirect
from django.core.exceptions import ValidationError
from .forms import UpdateStatusForm
from .forms import RescheduleAppointmentForm

# Create your views here.@login_required
def select_doctor(request):
    form = DoctorSelectionForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        appointment = form.save(commit=False)
        appointment.patient = request.user

        try:
            with transaction.atomic():  
                appointment.clean()
                appointment.save()
                appointment.slot.is_booked = True
                appointment.slot.save()
        except IntegrityError as e:
            form.add_error(None, str(e))
        else:
            return redirect('appointment_success')

    return render(request, 'appointment/select_doctor.html', {'form': form})

def load_slots(request):
    doctor_id = request.GET.get('doctor')
    slots_data = []

    if doctor_id:
        slots = AppointmentSlot.objects.filter(
            doctor_id=doctor_id,
            is_booked=False,
            date__gte=now().date()
        ).order_by('date', 'start_time')

        slots_data = [
            {"id": slot.id, "text": f"{slot.date} | {slot.start_time} - {slot.end_time}"}
            for slot in slots
        ]

    return JsonResponse(slots_data, safe=False)


def appointment_success(request):
    return render(request, 'appointment/success.html')


class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = "appointments/list.html"
    context_object_name = "appointments"

    def get_queryset(self):
        user = self.request.user
        print("Logged-in user:", user, user.role, user.username)  # <<-- add this

        if user.role == "PATIENT":
            return Appointment.objects.filter(patient=user).select_related('doctor', 'slot').order_by('-slot__date')

        if user.role == "DOCTOR":
            return Appointment.objects.filter(doctor=user).select_related('patient', 'slot').order_by('-slot__date')

        return Appointment.objects.all().select_related('patient', 'doctor', 'slot').order_by('-slot__date')

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


@login_required
def reschedule_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == 'POST':
        form = RescheduleAppointmentForm(request.POST, appointment=appointment)
        if form.is_valid():
            new_slot = form.cleaned_data['new_slot']
            reason = form.cleaned_data['reason']

            if appointment.status not in ["REQUESTED", "CONFIRMED"]:
                form.add_error(None, "Cannot reschedule an appointment in this state.")
            else:
                try:
                    appointment.reschedule(request.user, new_slot, reason)
                    messages.success(request, f"Appointment rescheduled successfully to {new_slot.date} at {new_slot.start_time}.")
                    return redirect('appointment_list')
                except ValidationError as e:
                    form.add_error(None, e.message)
    else:
        form = RescheduleAppointmentForm(appointment=appointment)

    return render(request, 'appointment/reschedule.html', {'form': form, 'appointment': appointment})


@login_required
def receptionist_check_in(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.user.role != "RECEPTIONIST":
        messages.error(request, "Only receptionist can check-in patients.")
        return redirect("appointment_list")

    try:
        appointment.check_in(request.user)
        messages.success(request, "Patient checked in successfully.")
    except ValidationError as e:
        messages.error(request, e.message)

    return redirect("appointment_list")

class DoctorQueueView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = "appointments/doctor_queue.html"
    context_object_name = "queue"

    def get_queryset(self):
        today = timezone.localdate()
        return (
            Appointment.objects.filter(
                doctor=self.request.user,
                status='CHECKED_IN',
                slot__date=today
            )
            .order_by('check_in_time')
            .select_related('patient', 'slot')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
    
    
    
@login_required
def create_consultation(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    # Only doctor allowed
    if request.user.role == "RECEPTIONIST":
        messages.error(request, "Receptionist cannot access medical records.")
        return redirect("appointment_list")
    if request.user.role != "DOCTOR":
        messages.error(request, "Only doctors can create consultations.")
        return redirect("appointment_list")

    # Must be completed
    if appointment.status != Appointment.Status.COMPLETED:
        messages.error(request, "Consultation can only be created for completed appointments.")
        return redirect("appointment_list")

    # Prevent duplicate consultation
    if hasattr(appointment, "consultation"):
        messages.warning(request, "Consultation already exists.")
        return redirect("appointment_list")

    if request.method == "POST":
        diagnosis = request.POST.get("diagnosis")
        notes = request.POST.get("notes")

        ConsultationRecord.objects.create(
            appointment=appointment,
            diagnosis=diagnosis,
            notes=notes
        )

        messages.success(request, "Consultation created successfully.")
        return redirect("appointment_list")

    return render(request, "appointments/create_consultation.html", {
        "appointment": appointment
    })

@login_required
def view_consultation(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    # Only patient owner allowed
    if request.user != appointment.patient:
        messages.error(request, "You are not allowed to view this consultation.")
        return redirect("appointment_list")

    if not hasattr(appointment, "consultation"):
        messages.warning(request, "No consultation available.")
        return redirect("appointment_list")

    return render(request, "appointments/view_consultation.html", {
        "consultation": appointment.consultation
    })