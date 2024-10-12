from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser
from django.core.mail import send_mail

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirm_password']

    def create(self, validated_data):
        if validated_data['password'] != validated_data.pop('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    def validate(self, data):
        email = data['email']
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_url = f"http://127.0.0.1:8000/password-reset-confirm/{uidb64}/{token}/"
            send_mail(
                'Password Reset Request',
                f'Here is your password reset link: {reset_url}',
                settings.EMAIL_HOST_USER,  # Set your own sender email address
                [user.email],
                fail_silently=False,
            )
            return data
        else:
            raise serializers.ValidationError("User with this email does not exist.")

    def save(self):
        # Optionally, if needed you can define any additional save logic here.
        pass

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = CustomUser.objects.get(id=uid)
            if not PasswordResetTokenGenerator().check_token(user, data['token']):
                raise serializers.ValidationError("Invalid token.")
            user.set_password(data['password'])
            user.save()
            return user
        except DjangoUnicodeDecodeError:
            raise serializers.ValidationError("Invalid token or user.")       
