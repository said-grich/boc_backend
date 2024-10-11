from django.urls import path
from .views import RegistrationView, LoginView, ProfileView, PasswordResetView, SetNewPasswordView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set_new_password'),
]
