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

def generate_otp():
    return str(random.randint(1000, 9999))  # Generate a 4-digit OTP

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    mobile_number = data.get('mobile_number')
    role = data.get('role')
    email = data.get('email')
    password = data.get('password')

    if User.objects.filter(username=mobile_number).exists():
        return Response({'error': 'This mobile number is already registered.'}, status=status.HTTP_400_BAD_REQUEST)

    otp = generate_otp()

    # Store registration data with initial resend_count = 0 ✅
    request.session['registration_data'] = {
        'mobile_number': mobile_number,
        'role': role,
        'email': email,
        'password': password,
        'resend_count': 0  # ✅ Do not count initial OTP as resend
    }
    request.session['otp'] = otp

    send_otp_via_msg91(mobile_number, otp)

    return Response({'message': 'OTP sent successfully.', 'otp': otp}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    entered_otp = request.data.get('otp')
    session_otp = request.session.get('otp')
    registration_data = request.session.get('registration_data')

    if not registration_data:
        return Response({'error': 'Session expired. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)

    if entered_otp != session_otp:
        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

    # OTP verified — now create User and Profile
    user = User.objects.create_user(
        username=registration_data['mobile_number'],
        email=registration_data['email'],
        password=registration_data['password']
    )

    is_verified = False if registration_data['role'] in ['builder', 'agent'] else True

    UserProfile.objects.create(
        user=user,
        mobile_number=registration_data['mobile_number'],
        role=registration_data['role'],
        is_verified=is_verified,
        is_otp_verified=True
    )

    # Clear session
    request.session.pop('registration_data', None)
    request.session.pop('otp', None)


    return Response({
        'message': 'OTP verified and user registered successfully.',
    }, status=status.HTTP_201_CREATED)



@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    registration_data = request.session.get('registration_data')

    if not registration_data:
        return Response({'error': 'Session expired. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)

    resend_count = registration_data.get('resend_count', 0)

    if resend_count >= 3:
        # ❌ Delete session data after exceeding limit
        request.session.pop('registration_data', None)
        request.session.pop('otp', None)

        return Response({
            'error': 'You have exceeded the maximum OTP resend attempts (3). Session has expired. Please register again.'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # ✅ Allow resend
    new_otp = generate_otp()
    registration_data['resend_count'] = resend_count + 1
    request.session['registration_data'] = registration_data
    request.session['otp'] = new_otp

    send_otp_via_msg91(registration_data['mobile_number'], new_otp)

    return Response({
        'message': f'OTP resent successfully! Attempt {resend_count + 1}/3',
        'otp': new_otp
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

            # Check if OTP is verified
            if not profile.is_otp_verified:
                otp = generate_otp()  # Generate a new OTP
                profile.otp = otp
                profile.save()
                send_otp_via_msg91(mobile_number, otp)
                return Response({'error': 'OTP_NOT_VERIFIED', 'message': 'OTP verification required.', 'otp': otp}, status=status.HTTP_403_FORBIDDEN)

            # Check if Builder or Agent is admin-approved
            if profile.role in ['builder', 'agent'] and not profile.is_verified:
                return Response({'message': 'Your account is awaiting admin approval.'}, status=status.HTTP_403_FORBIDDEN)

            # Issue tokens for authentication
            tokens = get_tokens_for_user(user)

            # Login user
            login(request, user)

            # If profile is not completed, instruct user to complete it
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
        user_profile.otp = otp
        user_profile.save()

        response = send_forget_otp_via_msg91(mobile_number, otp)

        if response.get("type") == "success":
            # Save session state for reset
            request.session['reset_mobile_number'] = mobile_number
            request.session['reset_otp'] = otp
            request.session['reset_resend_count'] = 0
            request.session.modified = True

            return Response({
                'message': 'OTP sent successfully',
                'otp': otp  # ✅ Only for debugging — remove in production
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to send OTP'}, status=status.HTTP_400_BAD_REQUEST)

    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
@permission_classes([AllowAny])
def resend_forget_otp(request):
    mobile_number = request.session.get('reset_mobile_number')

    if not mobile_number:
        return Response({'error': 'Session expired. Please request OTP again.'}, status=status.HTTP_400_BAD_REQUEST)

    resend_count = request.session.get('reset_resend_count', 0)

    if resend_count >= 3:
        # Clean up session after 3 attempts
        request.session.flush()
        return Response({'error': 'Max resend attempts reached. Please start over.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user_profile = UserProfile.objects.get(mobile_number=mobile_number)

        new_otp = generate_otp()
        user_profile.otp = new_otp
        user_profile.save()

        response = send_forget_otp_via_msg91(mobile_number, new_otp)

        if response.get("type") == "success":
            request.session['reset_otp'] = new_otp
            request.session['reset_resend_count'] = resend_count + 1
            request.session.modified = True

            return Response({
                'message': f'OTP resent successfully. Attempt {resend_count + 1}/3',
                'otp': new_otp
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to resend OTP'}, status=status.HTTP_400_BAD_REQUEST)

    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_verify_reset_otp(request):
    entered_otp = request.data.get('otp')
    session_mobile = request.session.get('reset_mobile_number')
    session_otp = request.session.get('reset_otp')

    if not session_mobile or not session_otp:
        return Response({'error': 'Session expired or OTP not requested.'}, status=status.HTTP_400_BAD_REQUEST)

    if entered_otp != session_otp:
        return Response({'error': 'Invalid OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_profile = UserProfile.objects.get(mobile_number=session_mobile)

        # Mark as verified in session
        request.session['reset_otp_verified'] = True
        request.session.modified = True

        return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)

    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    # Check if OTP was verified
    otp_verified = request.session.get('reset_otp_verified', False)
    mobile_number = request.session.get('reset_mobile_number')

    if not otp_verified or not mobile_number:
        return Response({'error': 'OTP not verified or session expired'}, status=status.HTTP_403_FORBIDDEN)

    new_password = request.data.get('new_password')

    if not new_password:
        return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_profile = UserProfile.objects.get(mobile_number=mobile_number)

        user_profile.user.set_password(new_password)
        user_profile.user.save()

        user_profile.otp = None
        user_profile.save()

        # Clear session
        request.session.flush()

        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)

    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


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