from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from .models import BlacklistedAccessToken

class BlockBlacklistedTokensMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
            if BlacklistedAccessToken.objects.filter(token=access_token).exists():
                return JsonResponse({'error': 'Token is blacklisted. Please log in again.'}, status=401)

        return self.get_response(request)
