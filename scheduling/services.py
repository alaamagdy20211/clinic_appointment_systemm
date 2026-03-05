from datetime import datetime, timedelta, date
from .models import AppointmentSlot, ScheduleException, DoctorSchedule

from datetime import datetime, timedelta, date
from .models import AppointmentSlot, ScheduleException, DoctorSchedule

def generate_slots_for_day(schedule_instance):
    if isinstance(schedule_instance, DoctorSchedule):
        current_date = date.today()  
    elif isinstance(schedule_instance, ScheduleException):
        current_date = schedule_instance.date
    else:
        return  

    day_off_exists = ScheduleException.objects.filter(
        doctor=schedule_instance.doctor,
        date=current_date,
        is_working_day=False
    ).exists()

    if day_off_exists:
        print(f"Skipping slot generation: {current_date} is marked as a day off.")
        return
    start_dt = datetime.combine(current_date, schedule_instance.start_time)
    end_dt = datetime.combine(current_date, schedule_instance.end_time)
    
    current_slot_start = start_dt
    slot_duration = timedelta(minutes=schedule_instance.slot_duration)
    buffer = timedelta(minutes=5) 

    slots_to_create = []
    while current_slot_start + slot_duration <= end_dt:
        slot_end = current_slot_start + slot_duration
        
        slots_to_create.append(
            AppointmentSlot(
                doctor=schedule_instance.doctor,
                date=current_date,
                start_time=current_slot_start.time(),
                end_time=slot_end.time(),
                is_booked=False
            )
        )
        
        current_slot_start = slot_end + buffer
    AppointmentSlot.objects.bulk_create(slots_to_create)

def CreateSlotsForNextMoth(schedule_instance):
    today = date.today()
    ne


def CancelSlotsForException(exception_instance):
    
    deleted_count, _ = AppointmentSlot.objects.filter(
        doctor=exception_instance.doctor,
        date=exception_instance.date,
        is_booked=False
    ).delete()
    print(f"Deleted {deleted_count} unbooked slots for exception on {exception_instance.date}")
    return 0

def DeleteOverdueExeptions():
    today = date.today()
    deleted_count, _ = ScheduleException.objects.filter(date__lt=today).delete()
    print(f"Deleted {deleted_count} overdue exceptions")
    return 0