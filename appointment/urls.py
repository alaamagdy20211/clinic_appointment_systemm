from django.urls import path
from .views import AppointmentListView,UpdateAppointmentStatusView
from . import views

urlpatterns = [
    path('list', AppointmentListView.as_view(), name='appointment_list'),
    path('updatestatus/<int:pk>',UpdateAppointmentStatusView.as_view(), name='appointment_updatestatus'),
    path('select-doctor/', views.select_doctor, name='select_doctor'),
    path('ajax/load-slots/', views.load_slots, name='ajax_load_slots'),
    path('success/', views.appointment_success, name='appointment_success'),
    path('reschedule/<int:pk>/', views.reschedule_appointment, name='reschedule_appointment'),
    path("check-in/<int:pk>/", views.receptionist_check_in, name="check_in_patient"),

]

