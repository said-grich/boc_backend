from rest_framework import generics, permissions, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from rest_framework.response import Response
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from .serializers import RegistrationSerializer, LoginSerializer, ProfileSerializer, PasswordResetSerializer, SetNewPasswordSerializer

from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

class RegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer

class LoginView(generics.GenericAPIView):
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

      

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
      
class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(email=serializer.validated_data['email'])
        token = PasswordResetTokenGenerator().make_token(user)
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        reset_link = f"http://localhost:3000/reset-password/{uidb64}/{token}/"
        
        send_mail(
            subject='Password Reset Request',
            message=f"Use the link below to reset your password:\n{reset_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        
        return Response({"detail": "Password reset link sent to your email."}, status=status.HTTP_200_OK)

class SetNewPasswordView(APIView):
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Password reset successful."},  status=status.HTTP_200_OK)