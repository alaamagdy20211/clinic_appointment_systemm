from django.urls import path
from .views import ScheduleListView, ScheduleCreateView

urlpatterns = [
    path('my-schedule/', ScheduleListView.as_view(), name='schedule-list'),
    path('my-schedule/create/', ScheduleCreateView.as_view(), name='schedule-create'),
]