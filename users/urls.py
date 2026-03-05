from django.urls import path
from .views import AdminUserListView, DeleteUserView, HomeRedirectView, PatientDashboardView, PatientProfileView, UserRegisterView, UserLoginView, UserLogoutView, AdminDashboardHomeView, CreateDoctorView, CreateReceptionistView, ExportAppointmentsCSV, DoctorDashboardView, ReceptionistDashboardView

urlpatterns = [
    path('', HomeRedirectView.as_view(), name='home'),
    path('dashboard/', PatientDashboardView.as_view(), name='patient_dashboard'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', PatientProfileView.as_view(), name='profile'),
    path('admin-dashboard/', AdminDashboardHomeView.as_view(), name='admin_dashboard'),
    path('admin-dashboard/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('admin-dashboard/users/create-doctor/', CreateDoctorView.as_view(), name='create_doctor'),
    path('admin-dashboard/users/create-receptionist/', CreateReceptionistView.as_view(), name='create_receptionist'),
    path('doctor/dashboard/', DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('receptionist/dashboard/', ReceptionistDashboardView.as_view(), name='receptionist_dashboard'),
    path('export-csv/', ExportAppointmentsCSV.as_view(), name='export_appointments_csv'),
    path('admin-dashboard/users/delete/<int:user_id>/', DeleteUserView.as_view(), name='delete_user'),
]