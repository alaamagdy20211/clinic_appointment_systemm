from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import transaction, IntegrityError
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .forms import DoctorSelectionForm
from .models import Appointment
from scheduling.models import AppointmentSlot

@login_required
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


