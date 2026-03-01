from django.urls import path
from . import views

urlpatterns = [
    path('select-doctor/', views.select_doctor, name='select_doctor'),
    path('ajax/load-slots/', views.load_slots, name='ajax_load_slots'),
    path('success/', views.appointment_success, name='appointment_success'),
]