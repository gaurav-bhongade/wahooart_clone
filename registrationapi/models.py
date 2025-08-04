from django.db import models

from django.db import models
from django.contrib.auth.models import User
import random
from . utils import send_otp_via_msg91

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('studio', 'Studio'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)
    is_otp_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=4, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.role == 'owner':
            self.is_verified = True
        super().save(*args, **kwargs)

    def generate_otp(self):
        """Generates a 4-digit OTP, saves it, and sends it via MSG91"""
        self.otp = str(random.randint(1000, 9999))
        self.save()

        send_otp_via_msg91(self.mobile_number, self.otp)
        return self.otp


    def __str__(self):
        return f"{self.user.username} - {self.role}"



class BlacklistedAccessToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
