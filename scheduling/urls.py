from django.urls import path
from .views import ScheduleListView, ScheduleCreateView, ScheduleExceptionCreateView

urlpatterns = [
    path('my-schedule/', ScheduleListView.as_view(), name='schedule-list'),
    path('my-schedule/create/', ScheduleCreateView.as_view(), name='schedule-create'),
    path('my-schedule/exception/create/', ScheduleExceptionCreateView.as_view(), name='schedule-exception-create'),
]