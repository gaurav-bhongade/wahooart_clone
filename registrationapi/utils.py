import requests

def send_otp_via_msg91(mobile_number, otp):
    API_KEY = "443046ADu2LnU3LbM67dc0b9fP1"  # Replace with your MSG91 API Key
    SENDER_ID = "ARTMLS"  # Replace with your MSG91 Sender ID
    TEMPLATE_ID = "67dd20d1d6fc05288f7d2852"  # Replace with your MSG91 Template ID
    URL = "https://control.msg91.com/api/v5/otp"

    payload = {
        "authkey": API_KEY,
        "mobile": f"+91{mobile_number}",  # Ensure correct mobile format
        "otp": otp,
        "sender": SENDER_ID,
        "template_id": TEMPLATE_ID,
        "otp_expiry": "10",  # OTP expires in 10 minutes
        "otp_length": "4",  # Ensure 4-digit OTP
        "realTimeResponse": "1"
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(URL, json=payload, headers=headers)
    
    # Print response details for debugging
    print(f"✅ MSG91 API Response Status: {response.status_code}")
    print(f"✅ MSG91 Response Text: {response.text}")

    if response.status_code == 200:
        print(f"✅ OTP sent to {mobile_number}")
    else:
        print(f"❌ Failed to send OTP: {response.text}")



def send_forget_otp_via_msg91(mobile_number, otp):
    MSG91_AUTH_KEY = "443046ADu2LnU3LbM67dc0b9fP1"
    MSG91_TEMPLATE_ID = "67dd3076d6fc0543fd750ec2"
    MSG91_OTP_EXPIRY = "10"
    """Sends OTP via MSG91 API for password reset"""
    url = "https://control.msg91.com/api/v5/otp"
    payload = {
        "authkey": MSG91_AUTH_KEY,
        "template_id": MSG91_TEMPLATE_ID,
        "mobile": f"91{mobile_number}",
        "otp": str(otp),
        "otp_expiry": MSG91_OTP_EXPIRY,
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_json = response.json()  # Ensure valid JSON response
        return response_json
    except requests.exceptions.RequestException as e:
        print(f"❌ MSG91 API Error: {e}")
        return {"type": "error", "message": "Failed to send OTP"}


def verify_otp_via_msg91(mobile_number, otp):
    API_KEY = "443046ADu2LnU3LbM67dc0b9fP1"
    url = f"https://control.msg91.com/api/v5/otp/verify"
    params = {
        "authkey": API_KEY,
        "otp": otp,
        "mobile": f"91{mobile_number}",
    }
    response = requests.get(url, params=params)
    print(f"✅ MSG91 Verify OTP Response: {response.text}")
    return response.json()  # Return response data


import requests

def resend_otp_via_msg91(mobile_number):
    MSG91_AUTH_KEY = "443046ADu2LnU3LbM67dc0b9fP1"  # Replace with your actual auth key
    MSG91_BASE_URL = "https://control.msg91.com/api/v5/otp"
    url = f"{MSG91_BASE_URL}/retry"
    params = {
        "authkey": MSG91_AUTH_KEY,
        "retrytype": "text",  # You can change it to "voice" if needed
        "mobile": f"91{mobile_number}",  # Country code is included
    }
    response = requests.get(url, params=params)
    print(f"✅ MSG91 Resend OTP Response: {response.text}")
    return response.json()  # Ensure this returns a dict with expected keys (e.g., {"type": "success"})




def resend_otp_retry(mobile_number):
    MSG91_AUTH_KEY = "443046ADu2LnU3LbM67dc0b9fP1"  # Replace with your actual auth key
    MSG91_BASE_URL = "https://control.msg91.com/api/v5/otp"
    """Function to resend OTP via MSG91"""
    url = f"{MSG91_BASE_URL}/retry"
    params = {
        "authkey": MSG91_AUTH_KEY,
        "retrytype": "text",  # You can change it to "voice" if needed
        "mobile": f"91{mobile_number}",  # Ensure country code is included
    }
    response = requests.get(url, params=params)
    print(f"✅ MSG91 Resend OTP Response: {response.text}")
    return response.json()




import random
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from django.conf import settings

OTP_SALT = "otp-salt"

def generate_otp():
    return str(random.randint(1000, 9999))

def get_serializer():
    return URLSafeTimedSerializer(settings.OTP_SECRET_KEY)

def generate_otp_token(mobile_number, otp, extra_data=None):
    s = get_serializer()
    payload = {'mobile': mobile_number, 'otp': otp}
    if extra_data:
        payload.update(extra_data)
    return s.dumps(payload, salt=OTP_SALT)

def verify_otp_token(token, entered_otp, max_age=settings.OTP_EXPIRY_SECONDS):
    s = get_serializer()
    try:
        data = s.loads(token, salt=OTP_SALT, max_age=max_age)
        if data.get('otp') == entered_otp:
            return data
        return False
    except Exception:
        return False

def decode_otp_token(token, max_age=settings.OTP_EXPIRY_SECONDS):
    s = get_serializer()
    try:
        return s.loads(token, salt=OTP_SALT, max_age=max_age)
    except SignatureExpired:
        return 'expired'
    except BadSignature:
        return None




