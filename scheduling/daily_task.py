from .models import ScheduleException, DoctorSchedule, AppointmentSlot
from django.utils import timezone
from datetime import date, timedelta
from .services import generate_slots_for_day

def DeleteOverdueExceptions():
    count =  ScheduleException.objects.filter(
        date__lt=timezone.now().date()
        ).delete()

    print(f"Deleted {count[0]} overdue exceptions.")

def DeleteOverdueSlots():
    count = AppointmentSlot.objects.filter(
        date__lt=timezone.now().date(),  
        is_booked=False
    ).delete()

    print(f"Deleted {count[0]} overdue slots.")

def GenerateSlotsForAllDoctors():
    today = date.today()
    target_date = today + timedelta(days=14)
    target_weekday = target_date.weekday()  
    previous_weekday = (target_weekday - 2) % 7

    # Get all schedules that match the weekday 14 days from now
    schedules = DoctorSchedule.objects.filter(day_of_week=previous_weekday)

    count = 0
    for schedule in schedules:
        # Check if there's a day-off exception for that specific date
        day_off_exists = ScheduleException.objects.filter(
            doctor=schedule.doctor,
            date=target_date,
            is_working_day=False
        ).exists()

        if day_off_exists:
            print(f"Skipping {schedule.doctor.username} on {target_date} — marked as day off.")
            continue

        # Check if slots already exist for that date
        slots_exist = AppointmentSlot.objects.filter(
            doctor=schedule.doctor,
            date=target_date
        ).exists()

        if slots_exist:
            print(f"Slots already exist for {schedule.doctor.username} on {target_date}, skipping.")
            continue

        # Reuse existing function to create slots
        generate_slots_for_day(schedule)
        count += 1

    print(f"Generated slots for {count} doctors on {target_date}.")