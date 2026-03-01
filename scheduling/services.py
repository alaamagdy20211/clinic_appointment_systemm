from datetime import datetime, timedelta, date
from .models import AppointmentSlot

def generate_slots_for_day(schedule_instance):
    current_date = date.today() 
    
    start_dt = datetime.combine(current_date, schedule_instance.start_time)
    end_dt = datetime.combine(current_date, schedule_instance.end_time)
    
    current_slot_start = start_dt
    duration = timedelta(minutes=schedule_instance.slot_duration)

    slots_to_create = []

    while current_slot_start + duration <= end_dt:
        slot_end = current_slot_start + duration
        slots_to_create.append(
            AppointmentSlot(
                doctor=schedule_instance.doctor,
                date=current_date,
                start_time=current_slot_start.time(),
                end_time=slot_end.time(),
                is_booked=False
            )
        )
        current_slot_start = slot_end
    AppointmentSlot.objects.bulk_create(slots_to_create)

def CancelSlotsForException(exception_instance):
    
    deleted_count, _ = AppointmentSlot.objects.filter(
        doctor=exception_instance.doctor,
        date=exception_instance.date,
        is_booked=False
    ).delete()
    print(f"Deleted {deleted_count} unbooked slots for exception on {exception_instance.date}")
    return 0