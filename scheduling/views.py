from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import DoctorSchedule, ScheduleException
from .forms import ScheduleForm, ScheduleExceptionForm
from .services import generate_slots_for_day, CancelSlotsForException, DeleteOverdueExeptions
from django.core.exceptions import ValidationError
class DoctorDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = DoctorSchedule
    template_name = 'scheduling/doctor_dashboard.html'

    
    def get_queryset(self):
        DeleteOverdueExeptions()
        return DoctorSchedule.objects.filter(doctor=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exceptions'] = ScheduleException.objects.filter(doctor=self.request.user)
        return context
    

    def test_func(self):
        
        print(f"User role: '{self.request.user.role}'")
        return self.request.user.role == 'DOCTOR'


class ScheduleListView(LoginRequiredMixin, ListView):  
    model = DoctorSchedule
    template_name = 'scheduling/schedule_list.html'

    def get_queryset(self):
        return DoctorSchedule.objects.filter(doctor=self.request.user)

    def test_func(self):
        print(f"User role: '{self.request.user.role}'")
        return self.request.user.role == 'DOCTOR'

class ScheduleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = DoctorSchedule
    form_class = ScheduleForm
    template_name = 'scheduling/schedule_form.html'
    success_url = reverse_lazy('schedule-list')

    def form_valid(self, form):
        form.instance.doctor = self.request.user
        try:
            generate_slots_for_day(form.instance)
        except ValidationError as exc:
            form.add_error(None, exc.message if hasattr(exc, 'message') else str(exc))
            return self.form_invalid(form)

        response = super().form_valid(form)
        return response

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance.doctor = self.request.user 
        return form

    def test_func(self):
        print(f"User role: '{self.request.user.role}'")
        return self.request.user.role == 'DOCTOR'

class ScheduleExceptionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ScheduleException
    form_class = ScheduleExceptionForm
    template_name = 'scheduling/schedule_exception_form.html'
    success_url = reverse_lazy('schedule-list')

    def form_valid(self, form):
        form.instance.doctor = self.request.user
        if form.instance.is_working_day:
            try:
                generate_slots_for_day(form.instance)
            except ValidationError as exc:
                form.add_error(None, exc.message if hasattr(exc, 'message') else str(exc))
                return self.form_invalid(form)
        else:
            CancelSlotsForException(form.instance)

        response = super().form_valid(form)
        return response

    def test_func(self):
        print(f"User role: '{self.request.user.role}'")
        return self.request.user.role == 'DOCTOR'