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



# import random
# import requests
# from django.core.cache import cache



# def resend_otp_retry(mobile_number):
#     """Function to resend OTP via MSG91 and store OTP manually"""

#     MSG91_AUTH_KEY = "443046ADu2LnU3LbM67dc0b9fP1"  # Replace with your actual auth key
#     MSG91_BASE_URL = "https://control.msg91.com/api/v5/otp"
    
#     otp = str(random.randint(1000, 9999))  # Generate new 4-digit OTP
    
#     # Store OTP in Django cache (valid for 5 minutes)
#     cache.set(f"otp_{mobile_number}", otp, timeout=300)

#     # Send OTP using MSG91
#     url = f"{MSG91_BASE_URL}/send"
#     params = {
#         "authkey": MSG91_AUTH_KEY,
#         "mobile": f"91{mobile_number}",
#         "otp": otp,  # Sending the OTP manually
#         "message": f"Your OTP for verification is {otp}. Do not share it with anyone.",
#         "sender": "MYAPP",  # Change this to your sender ID
#         "otp_length": 4,  # Ensures a 4-digit OTP
#     }
    
#     response = requests.get(url, params=params)
    
#     print(f"✅ MSG91 Resend OTP Response: {response.text}")
    
#     return {"type": "success", "otp": otp} if response.status_code == 200 else {"type": "error"}
