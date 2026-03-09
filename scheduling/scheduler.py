import os
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

def start_scheduler():
    if os.environ.get('RUN_MAIN') != 'true':
        return

    from .daily_task import DeleteOverdueExceptions, DeleteOverdueSlots, GenerateSlotsForAllDoctors

    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    scheduler.add_job(
        DeleteOverdueExceptions,
        'cron', hour=0, minute=0,
        id='delete_exceptions',
        replace_existing=True
    )
    scheduler.add_job(
        DeleteOverdueSlots,
        'cron', hour=0, minute=0,
        id='delete_slots',
        replace_existing=True
    )
    scheduler.add_job(
        GenerateSlotsForAllDoctors,
        'cron', hour=0, minute=0,
        id='generate_slots',
        replace_existing=True
    )

    scheduler.start()
    print("Scheduler started successfully.")