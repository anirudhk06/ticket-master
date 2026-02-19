from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.serializers import ChangePasswordSerializer


class CSRFTokenEndpoint(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        csrf_token = get_token(request)

        return Response({"csrf_token": str(csrf_token)})


class ChangePasswordEndpoint(APIView):
    def post(self, request):

        user = request.user

        serializer = ChangePasswordSerializer(data=request.data, context={"user": user})
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data["new_password"]

        user.set_password(password)
        user.is_password_autoset = False
        user.save(update_fields=["password", "is_password_autoset"])

        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass  # token already invalid or expired

        return Response({"message": "Password updated successfully"})
