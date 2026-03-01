# this is the users/views.py file
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User, DoctorProfile, PatientProfile, ReceptionistProfile
from .forms import PatientRegistrationForm, UserUpdateForm, PatientProfileUpdateForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView
from .models import User
from django.contrib.auth.mixins import LoginRequiredMixin

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
        # Pre-fill the forms with the patient's existing data
        user_form = UserUpdateForm(instance=request.user)
        profile_form = PatientProfileUpdateForm(instance=request.user.patient_profile)
        
        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        # Load the forms with the new submitted data
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = PatientProfileUpdateForm(request.POST, instance=request.user.patient_profile)

        # Save only if both forms are completely valid
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')

        # If invalid, reload the page showing the errors
        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, self.template_name, context)