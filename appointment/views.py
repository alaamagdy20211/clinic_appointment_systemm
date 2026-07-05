
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import transaction, IntegrityError
from django.utils.timezone import now
from django.utils import timezone
from users.permissions import PatientRequiredMixin
from .forms import DoctorSelectionForm
from .models import Appointment, ConsultationRecord
from scheduling.models import AppointmentSlot
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from .forms import UpdateStatusForm
from .forms import RescheduleAppointmentForm
from django.http import HttpResponseForbidden
from .models import AppointmentRescheduleLog
from django.views.generic import ListView, View, TemplateView
from django.db.models import Q



class SelectDoctorView(PatientRequiredMixin, View):
    template_name = "appointment/select_doctor.html"

    def get(self, request):
        form = DoctorSelectionForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = DoctorSelectionForm(request.POST)

        if form.is_valid():
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
                return redirect("appointment_success")

        return render(request, self.template_name, {"form": form})



class LoadSlotsView(LoginRequiredMixin, View):

    def get(self, request):
        doctor_id = request.GET.get("doctor")
        slots_data = []

        if doctor_id:
            slots = AppointmentSlot.objects.filter(
                doctor_id=doctor_id,
                is_booked=False,
                date__gte=now().date()
            ).order_by("date", "start_time")

            slots_data = [
                {
                    "id": slot.id,
                    "text": f"{slot.date} | {slot.start_time} - {slot.end_time}"
                }
                for slot in slots
            ]

        return JsonResponse(slots_data, safe=False)


def appointment_success(request):
    return render(request, 'appointment/success.html')


class AppointmentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "appointment/success.html"

class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = "appointments/list.html"
    context_object_name = "appointments"

    def get_queryset(self):
        user = self.request.user
        qs = Appointment.objects.select_related(
            'patient', 'doctor', 'slot').order_by('-slot__date')

        # Role filtering
        if user.role == "PATIENT":
            qs = qs.filter(patient=user)

        elif user.role == "DOCTOR":
            qs = qs.filter(doctor=user)

        # Staff filtering (Admin / Receptionist)
        if user.role in ["ADMIN", "RECEPTIONIST"]:

            # Filter by status
            status = self.request.GET.get("status")
            if status:
                qs = qs.filter(status=status)

            # Filter by doctor
            doctor = self.request.GET.get("doctor")
            if doctor:
                qs = qs.filter(doctor__id=doctor)

            # Filter by patient name
            patient = self.request.GET.get("patient")
            if patient:
                qs = qs.filter(patient__username__icontains=patient)

            # Date range filter
            start_date = self.request.GET.get("start_date")
            end_date = self.request.GET.get("end_date")

            if start_date:
                qs = qs.filter(slot__date__gte=start_date)

            if end_date:
                qs = qs.filter(slot__date__lte=end_date)

            # Search by ID or Patient name
            search = self.request.GET.get("q")
            if search:
                qs = qs.filter(
                    Q(id__icontains=search) |
                    Q(patient__username__icontains=search)
                )

        return qs

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




class RescheduleAppointmentView(LoginRequiredMixin, View):
    template_name = "appointment/reschedule.html"

    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        form = RescheduleAppointmentForm(appointment=appointment)
        return render(request, self.template_name, {
            "form": form,
            "appointment": appointment
        })

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        form = RescheduleAppointmentForm(request.POST, appointment=appointment)

        if form.is_valid():
            new_slot = form.cleaned_data["new_slot"]
            reason = form.cleaned_data["reason"]

            if appointment.status not in ["REQUESTED", "CONFIRMED"]:
                form.add_error(None, "Cannot reschedule an appointment in this state.")
            else:
                try:
                    appointment.reschedule(request.user, new_slot, reason)
                    messages.success(
                        request,
                        f"Appointment rescheduled successfully to {new_slot.date} at {new_slot.start_time}."
                    )
                    return redirect("appointment_list")
                except ValidationError as e:
                    form.add_error(None, e.message)

        return render(request, self.template_name, {
            "form": form,
            "appointment": appointment
        })



class ReceptionistCheckInView(LoginRequiredMixin, View):

    def post(self, request, pk):
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
    
    
    


class CreateConsultationView(LoginRequiredMixin, View):
    template_name = "appointments/create_consultation.html"

    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)

        if request.user.role == "RECEPTIONIST":
            messages.error(request, "Receptionist cannot access medical records.")
            return redirect("appointment_list")

        if request.user.role != "DOCTOR":
            messages.error(request, "Only doctors can create consultations.")
            return redirect("appointment_list")

        if appointment.status != Appointment.Status.CHECKED_IN:
            messages.error(request, "Consultation can only be created for checked_in appointments.")
            return redirect("appointment_list")

        if hasattr(appointment, "consultation"):
            messages.warning(request, "Consultation already exists.")
            return redirect("appointment_list")

        return render(request, self.template_name, {"appointment": appointment})

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)

        diagnosis = request.POST.get("diagnosis")
        notes = request.POST.get("notes")

        ConsultationRecord.objects.create(
            appointment=appointment,
            diagnosis=diagnosis,
            notes=notes
        )

        messages.success(request, "Consultation created successfully.")
        return redirect("appointment_list")
    


class ViewConsultationView(LoginRequiredMixin, View):
    template_name = "appointments/view_consultation.html"

    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)

        if request.user != appointment.patient:
            messages.error(request, "You are not allowed to view this consultation.")
            return redirect("appointment_list")

        if not hasattr(appointment, "consultation"):
            messages.warning(request, "No consultation available.")
            return redirect("appointment_list")

        return render(request, self.template_name, {
            "consultation": appointment.consultation
        })



class RescheduleLogAllView(LoginRequiredMixin, ListView):
    model = AppointmentRescheduleLog
    template_name = "appointment/reschedule_log_all.html"
    context_object_name = "logs"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "RECEPTIONIST":
            return HttpResponseForbidden("You are not allowed to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return AppointmentRescheduleLog.objects.select_related(
            "appointment", "old_slot", "new_slot", "changed_by"
        ).order_by("-timestamp")