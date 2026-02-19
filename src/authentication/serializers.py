from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.core.exceptions import ValidationError

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
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        attrs.pop("confirm_password")
        return attrs


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.strip().lower()


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()

    def validate_current_password(self, value):
        is_valid_password = self.context["user"].check_password(value)
        if is_valid_password:
            return value

        raise serializers.ValidationError("Invalid password")


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        user = getattr(self, "user", None) or self.context["user"]
        assert user is not None

        try:
            validate_password(attrs["new_password"], user)
        except Exception as e:
            raise serializers.ValidationError(
                {"new_password": serializers.as_serializer_error(e)}
            )

        return super().validate(attrs)


class PasswordRetypeSerializer(PasswordSerializer):
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if attrs.get("new_password") == attrs.get("confirm_password"):
            return super().validate(attrs)
        raise serializers.ValidationError("Password not matching.")


class ChangePasswordSerializer(CurrentPasswordSerializer, PasswordRetypeSerializer):
    pass
