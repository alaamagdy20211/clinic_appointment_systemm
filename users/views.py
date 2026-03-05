# this is the users/views.py file
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


from users.permissions import AdminRequiredMixin, PatientRequiredMixin, DoctorRequiredMixin, ReceptionistRequiredMixin
from .models import User, DoctorProfile, PatientProfile, ReceptionistProfile
from .forms import PatientRegistrationForm, UserUpdateForm, PatientProfileUpdateForm, DoctorRegistrationForm, ReceptionistRegistrationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, View
from django.contrib.auth.views import LoginView
from .models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from appointment.models import Appointment
from scheduling.models import ScheduleException, DoctorSchedule
from scheduling.services import DeleteOverdueExeptions
from django.utils import timezone
import csv
from django.http import HttpResponse
from datetime import datetime, timedelta, date
class UserRegisterView(CreateView):
    model = User
    form_class = PatientRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

class UserLoginView(LoginView):
    template_name = 'users/login.html'
    

class UserLogoutView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        request.session.flush()
        return redirect('login')

class PatientProfileView(PatientRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get(self, request):
        profile, _ = PatientProfile.objects.get_or_create(user=request.user)
        user_form = UserUpdateForm(instance=request.user)
        profile_form = PatientProfileUpdateForm(instance=profile)
        
        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        profile, _ = PatientProfile.objects.get_or_create(user=request.user)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = PatientProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')

        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, self.template_name, context)
    

class AdminDashboardHomeView(AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_doctors'] = User.objects.filter(role=User.Role.DOCTOR).count()
        context['total_patients'] = User.objects.filter(role=User.Role.PATIENT).count()
        context['total_receptionists'] = User.objects.filter(role=User.Role.RECEPTIONIST).count()
         # Appointment stats
        context['total_appointments'] = Appointment.objects.count()
        ###After adding the status in (appointments) models.py
        context['total_appointments'] = Appointment.objects.count()
        context['requested_appointments'] = Appointment.objects.filter(
            status=Appointment.Status.REQUESTED
        ).count()

        context['confirmed_appointments'] = Appointment.objects.filter(
            status=Appointment.Status.CONFIRMED
        ).count()

        context['checked_in_appointments'] = Appointment.objects.filter(
            status=Appointment.Status.CHECKED_IN
        ).count()

        context['completed_appointments'] = Appointment.objects.filter(
            status=Appointment.Status.COMPLETED
        ).count()

        context['cancelled_appointments'] = Appointment.objects.filter(
            status=Appointment.Status.CANCELLED
        ).count()

        return context
    
class AdminUserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'users/admin_user_list.html'
    context_object_name = 'users'
    
    def get_queryset(self):
        return User.objects.exclude(role=User.Role.ADMIN).order_by('role', 'username')


class CreateDoctorView(AdminRequiredMixin, CreateView):
    model = User
    form_class = DoctorRegistrationForm
    template_name = 'users/create_doctor.html'
    success_url = reverse_lazy('admin_user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Doctor created successfully.')
        return super().form_valid(form)


class CreateReceptionistView(AdminRequiredMixin, CreateView):
    model = User
    form_class = ReceptionistRegistrationForm
    template_name = 'users/create_receptionist.html'
    success_url = reverse_lazy('admin_user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Receptionist created successfully.')
        return super().form_valid(form)
    
class HomeRedirectView(LoginRequiredMixin, View):
    """Bounces the user to the correct dashboard based on their role."""
    def get(self, request, *args, **kwargs):
        role = request.user.role
        if role == User.Role.ADMIN:
            return redirect('admin_dashboard')
        elif role == User.Role.DOCTOR:
            # Heba will build the actual doctor view later, 
            # for now we can just route them to a placeholder or home.
            return redirect('doctor_dashboard') 
        elif role == User.Role.RECEPTIONIST:
            return redirect('receptionist_dashboard')
        else:
            # Default to patient
            return redirect('patient_dashboard')

class PatientDashboardView(PatientRequiredMixin, TemplateView):
    """The actual homepage for the Patient."""
    template_name = 'users/patient_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        upcoming = Appointment.objects.filter(
            patient=self.request.user,
            slot__date__gte=today,
            status__in=['REQUESTED', 'CONFIRMED', 'CHECKED_IN']
        ).select_related('doctor', 'slot').order_by('slot__date', 'slot__start_time')[:5]
        context['upcoming_appointments'] = upcoming
        context['upcoming_count'] = upcoming.count()
        return context


class DoctorDashboardView(DoctorRequiredMixin, TemplateView):
    template_name = 'users/doctor_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.request.user
        today = date.today()

        # ScheduleException.objects.filter(date__lt=today).delete()

        all_appts = Appointment.objects.filter(doctor=doctor).select_related('patient', 'slot')
        today_appts = all_appts.filter(slot__date=today).order_by('slot__start_time')

        # Build weekly list
        DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        schedule_days = {s.day_of_week: s for s in DoctorSchedule.objects.filter(doctor=doctor)}
        exceptions = ScheduleException.objects.filter(doctor=doctor).order_by('date')

        weekly = []
        for i, day_name in enumerate(DAYS):
            weekly.append({
                'day_name': day_name,
                'schedule': schedule_days.get(i),
                'exceptions': [e for e in exceptions if e.date.weekday() == i],
            })

        context['weekly'] = weekly
        context['exceptions'] = exceptions

        context['today_appointments'] = today_appts
        context['today_count'] = today_appts.count()
        context['total_count'] = all_appts.count()
        context['pending_count'] = all_appts.filter(status=Appointment.Status.REQUESTED).count()
        context['confirmed_count'] = all_appts.filter(status=Appointment.Status.CONFIRMED).count()
        context['checked_in_count'] = all_appts.filter(status=Appointment.Status.CHECKED_IN).count()
        context['completed_count'] = all_appts.filter(status=Appointment.Status.COMPLETED).count()
        context['today'] = today
        return context


class ReceptionistDashboardView(ReceptionistRequiredMixin, TemplateView):
    template_name = 'users/receptionist_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()

        all_appts = Appointment.objects.filter(slot__date=today).select_related('patient', 'doctor', 'slot').order_by('slot__start_time')

        context['today_appointments'] = all_appts
        context['today_count'] = all_appts.count()
        context['pending_count'] = all_appts.filter(status=Appointment.Status.REQUESTED).count()
        context['confirmed_count'] = all_appts.filter(status=Appointment.Status.CONFIRMED).count()
        context['checked_in_count'] = all_appts.filter(status=Appointment.Status.CHECKED_IN).count()
        context['completed_count'] = all_appts.filter(status=Appointment.Status.COMPLETED).count()
        context['total_patients'] = User.objects.filter(role=User.Role.PATIENT).count()
        context['total_doctors'] = User.objects.filter(role=User.Role.DOCTOR).count()
        context['today'] = today
        return context


class ExportAppointmentsCSV(View):
    def get(self, request, *args, **kwargs):
        # Check if user is admin using minix (bakry)
        

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="appointments.csv"'

        writer = csv.writer(response)
        writer.writerow(['slot', 'Patient', 'Doctor', 'Created At'])

        # Write data
        for a in Appointment.objects.all(): # change the data with the data in models.py in appoitments
            writer.writerow([
                a.slot,
                a.patient,
                a.doctor,
                a.created_at
            ])

        return response