from django.urls import path
from .views import LogoutView, RegistrationView, LoginView, ProfileViewSet, PasswordResetView, Forget_page
from django.urls import path, include

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileViewSet.as_view({'get': 'retrieve'}), name='profile'),  # For showing the user profile
    path('profile/update/', ProfileViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='profile_update'),  # For updating user profile
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('forgetPassword/', Forget_page, name='forget'),
]


