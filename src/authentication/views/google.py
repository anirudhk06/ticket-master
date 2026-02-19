import base64
import hashlib
import os
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

GOOGLE_AUTH_CACHE_KEY_PREFIX = "google:auth:state"
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET

User = get_user_model()

def generate_pkce_pair():
    """Generate PKCE code verifier and challenge pair."""
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    code_verifier = code_verifier.replace("=", "")

    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
    code_challenge = code_challenge.replace("=", "")

    return code_verifier, code_challenge

class GoogleOauthInitiateEndpoint(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        client_id = GOOGLE_CLIENT_ID

        state = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").replace("=", "")
        code_verifier, code_challenge = generate_pkce_pair()
        cache_key = f"{GOOGLE_AUTH_CACHE_KEY_PREFIX}:{state}"
        cache.set(cache_key, code_verifier, timeout=30)

        redirect_uri = f"""{"https" if request.is_secure() else "http"}://{request.get_host()}/auth/google/callback"""
        scope = " ".join(["openid", "email", "profile"])
        url_params = {
            "client_id": client_id,
            "scope": scope,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "code_challenge_method": "S256",
            "code_challenge": code_challenge,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }

        google_oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(url_params)}"

        return Response({"message": "Google Login", "auth_url": google_oauth_url})


class GoogleOauthCallbackEndpoint(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        
        code_verifier = cache.get(f"{GOOGLE_AUTH_CACHE_KEY_PREFIX}:{state}")

        if not code_verifier or code is None or state is None:
            return Response({"error": "Invalid or expired state"}, status=status.HTTP_400_BAD_REQUEST)
        
        token_endpoint = "https://accounts.google.com/o/oauth2/token"
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": f"{"https" if request.is_secure() else "http"}://{request.get_host()}/auth/google/callback",
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
        }

        response = requests.post(token_endpoint, data=token_data)
        response.raise_for_status()
        
        id_token_jwt = response.json().get("id_token")

        google_user_info = id_token.verify_oauth2_token(
            id_token_jwt,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=30,
        )

        if google_user_info["iss"] not in [
                "accounts.google.com",
            "https://accounts.google.com",
        ]:
            return Response({"error": "Invalid issuer"}, status=status.HTTP_400_BAD_REQUEST)

        email = google_user_info.get("email")

        if not email:
            return Response({
                "detail": "Email not found"
            }, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            email=email
        )

        if created:
            user.set_unusable_password()

        user.is_password_autoset = True
        user.last_login_medium = "google"
        user.last_login_ip = request.META.get("REMOTE_ADDR")
        user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
        
        user.save(
            update_fields=[
                "last_login_medium",
                "last_login_ip",
                "last_login_uagent",
            ]
        )
        
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )