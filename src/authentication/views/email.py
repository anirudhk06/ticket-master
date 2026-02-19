from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.serializers import (
    EmailLoginSerializer,
    EmailSignUpSerializer,
)

User = get_user_model()


class SignInAuthEndpoint(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data: dict[str, str] = serializer.validated_data

        user = authenticate(
            request, email=validated_data["email"], password=validated_data["password"]
        )

        if not user:
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.last_login_medium = "email"
        user.last_login_ip = request.META.get("REMOTE_ADDR")
        user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
        user.save(
            update_fields=["last_login_medium", "last_login_ip", "last_login_uagent"]
        )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "user_id": user.pk,
                    "username": user.username,
                    "email": user.email,
                },
            }
        )


class SignUpAuthEndpoint(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: dict[str, str] = serializer.validated_data

        if User.objects.filter(email__iexact=validated_data["email"]).exists():
            return Response(
                {"email": "Email already taken"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                user = User.objects.create(
                    email=validated_data["email"],
                    username=validated_data["email"].split("@")[0],
                )

                user.set_password(validated_data["password"])
                user.last_login_medium = "email"
                user.last_login_ip = request.META.get("REMOTE_ADDR")
                user.last_login_uagent = request.META.get("HTTP_USER_AGENT")
                user.save(
                    update_fields=[
                        "password",
                        "last_login_medium",
                        "last_login_ip",
                        "last_login_uagent",
                    ]
                )
        except Exception:
            return Response(
                {"detial": "Something went wrong please try again"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "User registration successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class RefreshTokenEndpoint(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token: str = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access = str(refresh.access_token)
        except:
            return Response(
                {"detail": "Invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"access": access})


class SignOutAuthEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except:
            return Response(
                {"detail": "Invalid token or expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Successfully logged out"},
            status=status.HTTP_205_RESET_CONTENT,
        )
