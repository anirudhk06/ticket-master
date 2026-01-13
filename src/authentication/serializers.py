from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from db.models import User


class EmailSignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs: dict):

        password: str = attrs["password"]
        confirm_password: str = attrs["confirm_password"]

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Password do not match."}
            )

        user = User(email=attrs["email"])

        try:
            validate_password(password, user)
        except Exception as e:
            raise serializers.ValidationError(
                {"password": serializers.as_serializer_error(e)}
            )

        attrs.pop("confirm_password")
        return attrs


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.strip().lower()
