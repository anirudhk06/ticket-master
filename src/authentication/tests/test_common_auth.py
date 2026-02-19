import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.views.common import (
    ChangePasswordEndpoint,
    CSRFTokenEndpoint,
)

User = get_user_model()


@pytest.fixture
def api_factory():
    return APIRequestFactory()


def test_csrf_success(api_factory):
    request = api_factory.get("/auth/csrf-token")

    response = CSRFTokenEndpoint.as_view()(request)

    assert response.status_code == 200
    assert "csrf_token" in response.data


@pytest.mark.django_db
def test_change_password(api_factory):
    user = User.objects.create(email="anirudh@gmail.com")
    user.set_password("Test@123")
    user.save()

    refresh = RefreshToken.for_user(user)

    request = api_factory.post(
        "/auth/change-password",
        {
            "current_password": "Test@123",
            "new_password": "New@12345678",
            "confirm_password": "New@12345678",
            "refresh": str(refresh),
        },
        format="json",
    )

    force_authenticate(request, user)

    response = ChangePasswordEndpoint.as_view()(request)

    user.refresh_from_db()

    assert response.status_code == 200
    assert user.check_password("New@12345678") is True
    assert user.is_password_autoset is False
    assert BlacklistedToken.objects.count() == 1