from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, View
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from .models import DoctorSchedule, AppointmentSlot
# from .services import generate_slots_for_day
from datetime import date, timedelta

# class ScheduleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):

# class ScheduleListView(ListView):
#     model = DoctorSchedule
#     template_name = 'scheduling/schedule_list.html'

#     def get_queryset(self):
#         return DoctorSchedule.objects.filter(doctor=self.request.user.doctor_profile)


class ScheduleListView(LoginRequiredMixin, ListView):  # Add the mixin here
    model = DoctorSchedule
    template_name = 'scheduling/schedule_list.html'

    def get_queryset(self):
        # Now this is safe because LoginRequiredMixin ensures user is authenticated
        return DoctorSchedule.objects.filter(doctor=self.request.user.doctor_profile)