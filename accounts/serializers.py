from rest_framework import serializers
from .models import CustomUser
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser
from django.core.mail import send_mail
import string
import random
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
    new_password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    current_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'profile_picture', 'new_password', 'confirm_password', 'current_password']
        extra_kwargs = {
        'email':{'required': False}, 
        'profile_picture':{'required': False},
        'username':{'required': False}}
        
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)

        # Handle password change
        new_password = validated_data.get('new_password')
        confirm_password = validated_data.get('confirm_password')
        current_password = validated_data.get('current_password')

        if new_password or confirm_password:
            if not current_password:
                raise serializers.ValidationError({"current_password": "Current password is required to set a new password."})

            if not instance.check_password(current_password):
                raise serializers.ValidationError({"current_password": "Current password is incorrect."})

            if new_password != confirm_password:
                raise serializers.ValidationError({"confirm_password": "New passwords do not match."})

            instance.set_password(new_password)

        # Handle profile picture upload if provided
        if 'profile_picture' in validated_data:
            instance.profile_picture = validated_data['profile_picture']
        
        instance.save()
        return instance

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("There is no user registered with this email address.")
        return value

    def generate_new_password(self, length=8):
        """Generate a random password with letters and digits."""
        characters = string.ascii_letters + string.digits
        new_password = ''.join(random.choice(characters) for i in range(length))
        return new_password

    def save(self):
        email = self.validated_data['email']
        user = CustomUser.objects.get(email=email)

        # Generate a new password
        new_password = self.generate_new_password()

        # Set the new password
        user.set_password(new_password)
        user.save()

        # Send the new password via email
        send_mail(
            subject="Your new password",
            message=f"Your new password is: {new_password}",
            from_email="bocisearch@gmail.com",  # Replace with your email
            recipient_list=[user.email],
        )