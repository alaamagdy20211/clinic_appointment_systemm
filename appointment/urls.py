from django.urls import path
from .views import AppointmentListView, UpdateAppointmentStatusView, DoctorQueueView, SelectDoctorView, LoadSlotsView, AppointmentSuccessView, RescheduleAppointmentView, ReceptionistCheckInView, CreateConsultationView, ViewConsultationView, RescheduleLogAllView

urlpatterns = [
    path('list/', AppointmentListView.as_view(), name='appointment_list'),
    path('updatestatus/<int:pk>/', UpdateAppointmentStatusView.as_view(), name='appointment_updatestatus'),
    path('select-doctor/', SelectDoctorView.as_view(), name='select_doctor'),
    path('ajax/load-slots/', LoadSlotsView.as_view(), name='ajax_load_slots'),
    path('success/', AppointmentSuccessView.as_view(), name='appointment_success'),
    path('reschedule/<int:pk>/', RescheduleAppointmentView.as_view(), name='reschedule_appointment'),
    path('check-in/<int:pk>/', ReceptionistCheckInView.as_view(), name='check_in_patient'),
    path('doctor/queue/', DoctorQueueView.as_view(), name='doctor_queue'),
    path('consultation/create/<int:pk>/', CreateConsultationView.as_view(), name='create_consultation'),
    path('consultation/view/<int:pk>/', ViewConsultationView.as_view(), name='view_consultation'),
    path('reschedule-logs/', RescheduleLogAllView.as_view(), name='reschedule_log_all'),
]