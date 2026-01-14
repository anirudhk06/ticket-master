from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.serializers import (
    EmailLoginSerializer,
    EmailSignUpSerializer,
)
from db.models import OrganizerProfile, User


class SignInAuthEndpoint(APIView):
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
        user.last_login_ip = self.request.META.get("REMOTE_ADDR")
        user.last_login_uagent = self.request.META.get("HTTP_USER_AGENT")
        user.save(
            update_fields=["last_login_medium", "last_login_ip", "last_login_uagent"]
        )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user_id": user.pk,
                "username": user.username,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


class SignUpAuthEndpoint(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EmailSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: dict[str, str] = serializer.validated_data
        print(validated_data)

        if User.objects.filter(email=validated_data["email"]).exists():
            return Response(
                {"email": "Email already taken"}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            user = User.objects.create(
                email=validated_data["email"],
                username=validated_data["email"].split("@")[0],
                display_name=validated_data["email"].split("@")[0],
            )

            user.set_password(validated_data["password"])
            user.last_login_medium = "email"
            user.last_login_ip = self.request.META.get("REMOTE_ADDR")
            user.last_login_uagent = self.request.META.get("HTTP_USER_AGENT")
            user.save(
                update_fields=[
                    "password",
                    "last_login_medium",
                    "last_login_ip",
                    "last_login_uagent",
                ]
            )

            OrganizerProfile.objects.create(user=user)

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
