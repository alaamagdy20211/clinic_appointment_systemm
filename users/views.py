# this is the users/views.py file
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


from users.permissions import AdminRequiredMixin, PatientRequiredMixin, PatientRequiredMixin
from .models import User, DoctorProfile, PatientProfile, ReceptionistProfile
from .forms import PatientRegistrationForm, UserUpdateForm, PatientProfileUpdateForm, DoctorRegistrationForm, ReceptionistRegistrationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, View
from django.contrib.auth.views import LoginView
from .models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from appointment.models import Appointment

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

class PatientProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get(self, request):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = PatientProfileUpdateForm(instance=request.user.patient_profile)
        
        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = PatientProfileUpdateForm(request.POST, instance=request.user.patient_profile)

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
        # context['completed_appointments'] = Appointment.objects.filter(status='COMPLETED').count()
        # context['cancelled_appointments'] = Appointment.objects.filter(status='CANCELLED').count()
        # context['no_show_appointments'] = Appointment.objects.filter(status='NO_SHOW').count()

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
    
    # Later, Janna will add a get_context_data method here to fetch 
    # the patient's upcoming appointments from the database.