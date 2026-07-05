#!/bin/sh

while ! nc -z db 5432; do
  sleep 1
done
python manage.py makemigrations

python manage.py migrate
exec gunicorn clinic_appointment.wsgi:application \
    --bind 0.0.0.0:8000