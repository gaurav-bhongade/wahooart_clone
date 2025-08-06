from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from . models import UserProfile
import random
from . serializers import UserProfileSerializer
from . utils import send_otp_via_msg91, verify_otp_via_msg91, resend_otp_via_msg91, send_forget_otp_via_msg91, resend_otp_retry
from . models import BlacklistedAccessToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from .utils import generate_otp_token, verify_otp_token

from django.conf import settings
from itsdangerous import URLSafeTimedSerializer



def generate_otp():
    return str(random.randint(1000, 9999))


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile
from .utils import generate_otp, generate_otp_token, verify_otp_token, send_otp_via_msg91, get_tokens_for_user


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Step 1: Send OTP with user data embedded in token (no user created yet)
    """
    mobile_number = request.data.get('mobile_number')
    password = request.data.get('password')
    role = request.data.get('role')

    if not all([mobile_number, password, role]):
        return Response({'error': 'Mobile number, password, and role are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=mobile_number).exists():
        return Response({'error': 'Mobile number already registered'}, status=status.HTTP_400_BAD_REQUEST)

    otp = generate_otp()
    otp_token = generate_otp_token(mobile_number, otp, extra_data={'password': password, 'role': role})

    send_otp_via_msg91(mobile_number, otp)

    return Response({
        'message': 'OTP sent successfully.',
        'otp_token': otp_token,
        'otp': otp  # ⚠️ REMOVE in production!
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Step 2: Verify OTP and create user
    """
    entered_otp = request.data.get('otp')
    mobile_number = request.data.get('mobile_number')
    otp_token = request.data.get('otp_token')

    if not all([entered_otp, mobile_number, otp_token]):
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    # Verify token and extract payload
    payload = verify_otp_token(otp_token, entered_otp)

    if not payload:
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)

    if payload.get('mobile') != mobile_number:
        return Response({'error': 'Mobile number mismatch'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=mobile_number).exists():
        return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # Extract data from token
    password = payload.get('password')
    role = payload.get('role')

    # Create user
    user = User.objects.create_user(
        username=mobile_number,
        password=password
    )

    is_verified = False if role == 'studio' else True

    UserProfile.objects.create(
        user=user,
        mobile_number=mobile_number,
        role=role,
        is_verified=is_verified,
        is_otp_verified=True
    )

    tokens = get_tokens_for_user(user)

    return Response({
        'message': 'OTP verified and user registered successfully',
        'tokens': tokens
    }, status=status.HTTP_201_CREATED)







from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

# Helper to get serializer
def get_serializer():
    return URLSafeTimedSerializer(settings.OTP_SECRET_KEY, salt="otp-salt")

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    mobile_number = request.data.get('mobile_number')
    old_token = request.data.get('otp_token')

    if not old_token:
        return Response({'error': 'Missing OTP token'}, status=status.HTTP_400_BAD_REQUEST)

    s = get_serializer()

    try:
        data = s.loads(old_token, max_age=300)  # optional: set expiry (in seconds)
    except SignatureExpired:
        return Response({'error': 'OTP token expired'}, status=status.HTTP_400_BAD_REQUEST)
    except BadSignature:
        return Response({'error': 'Invalid OTP token'}, status=status.HTTP_400_BAD_REQUEST)

    role = data.get('role')
    email = data.get('email')
    password = data.get('password')
    resend_count = data.get('resend_count', 0)

    if resend_count >= 3:
        return Response({'error': 'Max resend attempts reached. Please register again.'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS)

    new_otp = generate_otp()
    new_data = {
        'mobile_number': mobile_number,
        'otp': new_otp,
        'role': role,
        'email': email,
        'password': password,
        'resend_count': resend_count + 1
    }

    new_token = s.dumps(new_data)
    send_otp_via_msg91(mobile_number, new_otp)

    return Response({
        'message': f'OTP resent. Attempt {resend_count + 1}/3',
        'otp_token': new_token,
        'otp': new_otp  # ⚠️ Remove in production
    }, status=status.HTTP_200_OK)





@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    mobile_number = request.data.get('mobile_number')
    password = request.data.get('password')

    user = authenticate(username=mobile_number, password=password)
    if user:
        try:
            profile = UserProfile.objects.get(user=user)

            if not profile.is_otp_verified:
                otp = generate_otp()
                profile.otp = otp
                profile.save()
                otp_token = generate_otp_token(mobile_number, otp)
                send_otp_via_msg91(mobile_number, otp)
                return Response({
                    'error': 'OTP_NOT_VERIFIED',
                    'message': 'OTP verification required.',
                    'otp': otp,  # ⚠️ Remove in production
                    'otp_token': otp_token
                }, status=status.HTTP_403_FORBIDDEN)

            if profile.role in ['builder', 'agent'] and not profile.is_verified:
                return Response({'message': 'Your account is awaiting admin approval.'}, status=status.HTTP_403_FORBIDDEN)

            tokens = get_tokens_for_user(user)
            login(request, user)

            if not profile.profile_completed:
                return Response({'message': 'Login successful, complete your profile.', 'tokens': tokens, 'redirect': 'complete_profile'}, status=status.HTTP_200_OK)

            return Response({'message': 'Login successful', 'tokens': tokens, 'redirect': 'home'}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({'error': 'No profile found for this user.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_profile(request):
    user = request.user
    profile = user.userprofile

    user.first_name = request.data.get('first_name', user.first_name)
    user.last_name = request.data.get('last_name', user.last_name)
    user.email = request.data.get('email', user.email)
    user.save()

    profile_picture = request.FILES.get('profile_picture')
    if profile_picture:
        profile.profile_picture = profile_picture
    
    profile.profile_completed = True
    profile.save()

    return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllowAny])
def forget_password_request(request):
    mobile_number = request.data.get('mobile_number')

    try:
        user_profile = UserProfile.objects.get(mobile_number=mobile_number)
        otp = generate_otp()
        otp_token = generate_otp_token(mobile_number, otp, expires_sec=300)

        response = send_forget_otp_via_msg91(mobile_number, otp)

        if response.get("type") == "success":
            return Response({
                'message': 'OTP sent successfully',
                'otp_token': otp_token,
                'otp': otp  # ⚠️ Remove in prod
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to send OTP'}, status=status.HTTP_400_BAD_REQUEST)

    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)





from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_forget_otp(request):
    mobile_number = request.data.get('mobile_number')
    old_token = request.data.get('otp_token')

    if not old_token:
        return Response({'error': 'Missing OTP token'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        s = URLSafeTimedSerializer(settings.OTP_SECRET_KEY)
        data = s.loads(old_token, max_age=300)  # Token valid for 5 mins
    except SignatureExpired:
        return Response({'error': 'OTP token has expired'}, status=status.HTTP_400_BAD_REQUEST)
    except BadSignature:
        return Response({'error': 'Invalid OTP token'}, status=status.HTTP_400_BAD_REQUEST)

    resend_count = data.get('resend_count', 0)

    if resend_count >= 3:
        return Response({'error': 'Max resend attempts reached. Please try again later.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user_profile = UserProfile.objects.get(mobile_number=mobile_number)
        new_otp = generate_otp()
        new_token_data = {
            'mobile_number': mobile_number,
            'otp': new_otp,
            'resend_count': resend_count + 1
        }

        s = URLSafeTimedSerializer(settings.OTP_SECRET_KEY)
        new_token = s.dumps(new_token_data)

        response = send_forget_otp_via_msg91(mobile_number, new_otp)

        if response.get("type") == "success":
            return Response({
                'message': f'OTP resent successfully. Attempt {resend_count + 1}/3',
                'otp_token': new_token,
                'otp': new_otp  # ⚠️ Remove in production
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to resend OTP'}, status=status.HTTP_400_BAD_REQUEST)

    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)





@api_view(['POST'])
@permission_classes([AllowAny])
def api_verify_reset_otp(request):
    mobile_number = request.data.get('mobile_number')
    entered_otp = request.data.get('otp')
    otp_token = request.data.get('otp_token')

    verified_mobile = verify_otp_token(otp_token, entered_otp)

    if not verified_mobile or verified_mobile != mobile_number:
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)

    # Send back a new token that proves OTP was verified
    verified_token = generate_otp_token(mobile_number, entered_otp, expires_sec=600, extra_data={"verified": True})

    return Response({
        'message': 'OTP verified successfully',
        'verified_token': verified_token
    }, status=status.HTTP_200_OK)




from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    mobile_number = request.data.get('mobile_number')
    new_password = request.data.get('new_password')
    verified_token = request.data.get('verified_token')

    if not new_password or not verified_token:
        return Response({'error': 'Missing password or verification token'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        s = URLSafeTimedSerializer(settings.OTP_SECRET_KEY)
        data = s.loads(verified_token, max_age=300)  # Token is valid for 5 minutes

        if data.get('mobile') != mobile_number or not data.get('verified'):
            return Response({'error': 'Token invalid or mismatched'}, status=status.HTTP_403_FORBIDDEN)

        user_profile = UserProfile.objects.get(mobile_number=mobile_number)
        user_profile.user.set_password(new_password)
        user_profile.user.save()

        user_profile.otp = None
        user_profile.save()

        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)

    except SignatureExpired:
        return Response({'error': 'Token has expired'}, status=status.HTTP_403_FORBIDDEN)
    except BadSignature:
        return Response({'error': 'Invalid token signature'}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """Retrieve user profile details"""
    user_profile = request.user.userprofile
    serializer = UserProfileSerializer(user_profile)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    """Update user profile information"""
    user_profile = request.user.userprofile
    user = request.user

    user.first_name = request.data.get("first_name", user.first_name)
    user.last_name = request.data.get("last_name", user.last_name)
    user.email = request.data.get("email", user.email)
    user.save()

    user_profile.mobile_number = request.data.get("mobile_number", user_profile.mobile_number)

    if "profile_picture" in request.FILES:
        user_profile.profile_picture = request.FILES["profile_picture"]

    user_profile.save()

    serializer = UserProfileSerializer(user_profile)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_pic(request):
    """Upload or update profile picture"""
    user_profile = request.user.userprofile

    if 'profile_picture' in request.FILES:
        user_profile.profile_picture = request.FILES['profile_picture']
        user_profile.save()
        return Response({"message": "Profile picture updated successfully!"}, status=status.HTTP_200_OK)

    return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    try:
        auth_header = request.headers.get('Authorization')
        
        # ✅ Extract access token from header
        if auth_header and auth_header.startswith('Bearer '):
            access_token_str = auth_header.split(' ')[1]
        else:
            return Response({"error": "Access token is required."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Decode access token to get user ID
        try:
            access_token = AccessToken(access_token_str)
            user_id = access_token.payload.get('user_id')
        except Exception:
            return Response({"error": "Invalid access token."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Blacklist the access token
        BlacklistedAccessToken.objects.create(token=access_token_str)

        # ✅ Find and blacklist the corresponding refresh token
        outstanding_tokens = OutstandingToken.objects.filter(user_id=user_id)
        for token in outstanding_tokens:
            try:
                RefreshToken(token.token).blacklist()
            except Exception:
                pass  # If already blacklisted, ignore

        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def edit_profile_api(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        user = request.user
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.email = request.data.get("email", user.email)
        user.save()

        user_profile.mobile_number = request.data.get("mobile_number", user_profile.mobile_number)
        
        if request.FILES.get("profile_picture"):
            user_profile.profile_picture = request.FILES["profile_picture"]

        user_profile.save()
        return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_pic_api(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.FILES.get("profile_picture"):
        user_profile.profile_picture = request.FILES["profile_picture"]
        user_profile.save()
        return Response({"message": "Profile picture uploaded successfully"}, status=status.HTTP_200_OK)

    return Response({"error": "No image uploaded"}, status=status.HTTP_400_BAD_REQUEST)


from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_account(request):
    try:
        user = request.user
        user.delete()  # This will also delete UserProfile if on_delete=models.CASCADE
        return Response({"message": "User account deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Something went wrong while deleting the account."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


