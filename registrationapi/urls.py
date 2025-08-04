from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
    path('register/', register, name='api-register'),
    path('verify-otp/', verify_otp, name='api-verify_otp'),
    path('resend-otp/', resend_otp, name='api-resend_otp'),
    path('login/', user_login, name='api-user-login'),
    path('profile/complete/', complete_profile, name='api-complete-profile'),
    path('forget-password/', forget_password_request, name='api-forget-password'),
    path('resend-reset-otp/', resend_forget_otp, name='api-resend-reset-otp'),
    path('verify-reset-otp/', api_verify_reset_otp, name='api-verify-reset-otp'),
    path('reset-password/', reset_password, name='api-reset-password'),
    path('profile/', profile_view, name='api-profile-view'),
    path('profile/edit/', edit_profile, name='api-edit-profile'),
    path('profile/upload-pic/', upload_profile_pic, name='api-upload-profile-pic'),
    path('logout/', user_logout, name='api-user-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/edit-profile/', edit_profile_api, name='edit-profile-api'),
    path('api/upload-profile-pic/', upload_profile_pic_api, name='upload-profile-pic-api'),
]
