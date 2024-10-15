from django.shortcuts import render
from rest_framework import generics, permissions, viewsets
from accounts.serializers import PasswordResetSerializer, RegistrationSerializer, LoginSerializer, ProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from rest_framework.response import Response
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import AllowAny


class RegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            # Check if user exists with the given email
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'Invalid credentials: email not found'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user (check password)
        if not user.check_password(password):
            return Response({'detail': 'Invalid credentials: wrong password'}, status=status.HTTP_400_BAD_REQUEST)

        # If credentials are correct, generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email,
        }, status=status.HTTP_200_OK)



def search_page(request):
    return render(request, 'search-page.html')

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch']  # Allow GET for fetching profile, PUT/PATCH for updates

    def get_queryset(self):
        # Return the current logged-in user's profile only
        return CustomUser.objects.filter(id=self.request.user.id)

    def retrieve(self, request, *args, **kwargs):
        # Get the current user's profile information (username, email, profile picture)
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        # Update the profile (username, email, password, confirm password)
        partial = kwargs.pop('partial', False)  # Check if it's a partial update
        instance = self.request.user
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        # This method will handle PATCH requests specifically
        return self.update(request, *args, **kwargs)  # Call the update method
def Forget_page(request):
    return render(request, 'Forgotpassword.html')

class PasswordResetView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access for password reset

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "A new password has been sent to your email."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        try:
            # Get the refresh token from the request
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            # Blacklist the refresh token
            token.blacklist()
            
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)