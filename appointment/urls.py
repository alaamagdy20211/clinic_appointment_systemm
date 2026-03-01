from django.urls import path
from .views import AppointmentListView,UpdateAppointmentStatusView

urlpatterns = [
    path('list', AppointmentListView.as_view(), name='appointment_list'),
    path('updatestatus/<int:pk>',UpdateAppointmentStatusView.as_view(), name='appointment_updatestatus'),
]