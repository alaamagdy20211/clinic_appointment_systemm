# this is the users/views.py file
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User, DoctorProfile, PatientProfile, ReceptionistProfile
from .forms import PatientRegistrationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from .models import User

class UserRegisterView(CreateView):
    model = User
    form_class = PatientRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

class UserLoginView(LoginView):
    template_name = 'users/login.html'

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')