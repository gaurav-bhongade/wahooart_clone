from rest_framework import serializers
from django.contrib.auth.models import User
from . models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    
    user = UserSerializer()
    
    class Meta:
        model = UserProfile
        fields = ['user', 'mobile_number', 'role', 'is_verified', 'is_otp_verified', 'profile_picture', 'profile_completed', 'created_at', 'updated_at']
