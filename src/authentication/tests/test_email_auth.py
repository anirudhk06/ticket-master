from concurrent.futures import ThreadPoolExecutor

import pytest
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.views.email import (
    RefreshTokenEndpoint,
    SignInAuthEndpoint,
    SignOutAuthEndpoint,
    SignUpAuthEndpoint,
)

User = get_user_model()


@pytest.fixture
def api_factory():
    return APIRequestFactory()


@pytest.mark.django_db
def test_signup_success(api_factory):
    request = api_factory.post(
        "/auth/sign-up",
        {
            "email": "user@test.com",
            "password": "Test@123",
            "confirm_password": "Test@123",
        },
        format="json",
    )

    response = SignUpAuthEndpoint.as_view()(request)
    assert response.status_code == 201


@pytest.mark.django_db(transaction=True)
def test_concurrent_signup_same_email():
    client = APIClient()

    payload = {
        "email": "user@test.com",
        "password": "Test@123",
        "confirm_password": "Test@123",
    }

    def signup():
        return client.post("/auth/sign-up", payload, format="json")

    with ThreadPoolExecutor(max_workers=5) as executor:
        responses = list(executor.map(lambda _: signup(), range(5)))

    success_response = [r for r in responses if r.status_code == 201]
    failed_responses = [r for r in responses if r.status_code == 400]

    assert len(success_response) == 1
    assert len(failed_responses) == 4
    assert User.objects.filter(email="user@test.com").count() == 1


@pytest.mark.django_db
def test_signup_duplicate_email(api_factory):
    User.objects.create_user(
        email="user@test.com",
        username="user",
        password="Test@123",
    )

    request = api_factory.post(
        "/auth/sign-up",
        {
            "email": "user@test.com",
            "password": "Test@123",
            "confirm_password": "Test@123",
        },
        format="json",
    )

    response = SignUpAuthEndpoint.as_view()(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_signup_password_mismatch(api_factory):
    request = api_factory.post(
        "/auth/sign-up",
        {
            "email": "user@test.com",
            "password": "StrongPass@123",
            "confirm_password": "WrongPass@123",
        },
        format="json",
    )

    response = SignUpAuthEndpoint.as_view()(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_signup_weak_password(api_factory):
    request = api_factory.post(
        "/auth/sign-up",
        {
            "email": "user@test.com",
            "password": "123",
            "confirm_password": "123",
        },
        format="json",
    )

    response = SignUpAuthEndpoint.as_view()(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_signup_returns_tokens(api_factory):
    request = api_factory.post(
        "/auth/sign-up",
        {
            "email": "user@test.com",
            "password": "StrongPass@123",
            "confirm_password": "StrongPass@123",
        },
        format="json",
    )

    response = SignUpAuthEndpoint.as_view()(request)
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_signup_sets_last_login_medium(api_factory):
    request = api_factory.post(
        "/auth/sign-up",
        {
            "email": "user@test.com",
            "password": "StrongPass@123",
            "confirm_password": "StrongPass@123",
        },
        format="json",
    )

    SignUpAuthEndpoint.as_view()(request)
    user = User.objects.get(email="user@test.com")

    assert user.last_login_medium == "email"


@pytest.mark.django_db
def test_signin_success(api_factory):
    user = User.objects.create(email="user@test.com", last_login_medium="email")
    user.set_password("StrongPass@123")
    user.save()

    request = api_factory.post(
        "/auth/sign-in",
        {"email": "user@test.com", "password": "StrongPass@123"},
        format="json",
    )

    response = SignInAuthEndpoint.as_view()(request)

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data
    assert response.data["user_id"] == user.pk


@pytest.mark.django_db
def test_signin_wrong_password(api_factory):
    user = User.objects.create(email="user@test.com")
    user.set_password("StrongPass@123")
    user.save()

    request = api_factory.post(
        "/auth/sign-in",
        {"email": "user@test.com", "password": "WrongPass@123"},
        format="json",
    )

    response = SignInAuthEndpoint.as_view()(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_signin_non_existent_user(api_factory):
    request = api_factory.post(
        "/auth/sign-in",
        {"email": "user@test.com", "password": "StrongPass@123"},
        format="json",
    )

    response = SignInAuthEndpoint.as_view()(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_logout_success(api_factory):
    user = User.objects.create_user(
        email="user@test.com",
        username="user",
        password="StrongPass@123",
    )

    refresh = RefreshToken.for_user(user)

    request = api_factory.post(
        "/auth/sign-out/",
        {"refresh": str(refresh)},
        format="json",
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
    )

    response = SignOutAuthEndpoint.as_view()(request)

    assert response.status_code == 205
    assert BlacklistedToken.objects.count() == 1


@pytest.mark.django_db
def test_refresh_token_success(api_factory):
    user = User.objects.create(email="user@test.com")
    user.set_password("StrongPass@123")
    user.save()

    refresh = RefreshToken.for_user(user)

    request = api_factory.post(
        "/auth/refresh-token",
        {"refresh": str(refresh)},
        format="json",
    )

    response = RefreshTokenEndpoint.as_view()(request)

    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_refresh_token_missing(api_factory):
    request = api_factory.post(
        "/auth/refresh-token",
        {},
        format="json",
    )

    response = RefreshTokenEndpoint.as_view()(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_refresh_token_invalid(api_factory):
    request = api_factory.post(
        "/auth/refresh-token",
        {"refresh": "invalid.token.value"},
        format="json",
    )

    response = RefreshTokenEndpoint.as_view()(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_refresh_token_blacklisted(api_factory):
    user = User.objects.create(email="user@test.com")
    user.set_password("StrongPass@123")
    user.save()

    refresh = RefreshToken.for_user(user)
    refresh.blacklist()

    request = api_factory.post(
        "/auth/refresh-token",
        {"refresh": str(refresh)},
        format="json",
    )

    response = RefreshTokenEndpoint.as_view()(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_refresh_token_not_blacklisted_on_success(api_factory):
    user = User.objects.create(email="user@test.com")
    user.set_password("StrongPass@123")
    user.save()

    refresh = RefreshToken.for_user(user)

    request = api_factory.post(
        "/auth/refresh-token",
        {"refresh": str(refresh)},
        format="json",
    )

    RefreshTokenEndpoint.as_view()(request)

    assert BlacklistedToken.objects.count() == 0