from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.views.email import (
    SignInAuthEndpoint,
    SignOutAuthEndpoint,
    SignUpAuthEndpoint,
    RefreshTokenEndpoint,
)
from db.models import User


class TestSignUpAuthentication(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.authentication = JWTAuthentication()

    def test_signup_success(self):
        request = self.factory.post(
            "/auth/sign-up",
            {
                "email": "user@test.com",
                "password": "Test@123",
                "confirm_password": "Test@123",
            },
            format="json",
        )

        response = SignUpAuthEndpoint.as_view()(request)
        self.assertEqual(response.status_code, 201)

    def test_signup_duplicate_email(self):
        User.objects.create_user(
            email="user@test.com",
            username="user",
            password="Test@123",
        )

        request = self.factory.post(
            "/auth/sign-up",
            {
                "email": "user@test.com",
                "password": "Test@123",
                "confirm_password": "Test@123",
            },
            format="json",
        )

        response = SignUpAuthEndpoint.as_view()(request)

        self.assertEqual(response.status_code, 400)

    def test_signup_password_mismatch(self):
        request = self.factory.post(
            "/auth/sign-up",
            {
                "email": "user@test.com",
                "password": "StrongPass@123",
                "confirm_password": "WrongPass@123",
            },
            format="json",
        )
        response = SignUpAuthEndpoint.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_signup_weak_password(self):
        request = self.factory.post(
            "/auth/sign-up",
            {
                "email": "user@test.com",
                "password": "123",
                "confirm_password": "123",
            },
            format="json",
        )
        response = SignUpAuthEndpoint.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_signup_returns_tokens(self):
        request = self.factory.post(
            "/auth/sign-up",
            {
                "email": "user@test.com",
                "password": "StrongPass@123",
                "confirm_password": "StrongPass@123",
            },
            format="json",
        )
        response = SignUpAuthEndpoint.as_view()(request)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_last_login_medium(self):
        request = self.factory.post(
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

        self.assertEqual(user.last_login_medium, "email")


class TestSignInAuthentication(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.authentication = JWTAuthentication()

    def test_signin_success(self):
        user = User.objects.create(email="user@test.com", last_login_medium="email")
        user.set_password("StrongPass@123")
        user.save()

        request = self.factory.post(
            "/auth/sign-in",
            {"email": "user@test.com", "password": "StrongPass@123"},
            format="json",
        )

        response = SignInAuthEndpoint.as_view()(request)

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(user.last_login_medium, "email")
        self.assertEqual(user.pk, response.data["user_id"])
        self.assertEqual(response.status_code, 200)

    def test_wrong_password(self):
        user = User.objects.create(
            email="user@test.com",
        )
        user.set_password("StrongPass@123")
        user.save()

        request = self.factory.post(
            "/auth/sign-in",
            {"email": "user@test.com", "password": "WrongPass@123"},
            format="json",
        )

        response = SignInAuthEndpoint.as_view()(request)

        self.assertEqual(response.status_code, 400)

    def test_signin_non_existent_user(self):
        request = self.factory.post(
            "/auth/sign-in",
            {"email": "user@test.com", "password": "StrongPass@123"},
            format="json",
        )

        response = SignInAuthEndpoint.as_view()(request)
        self.assertEqual(response.status_code, 400)


class TestSignOutAuthentication(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.authentication = JWTAuthentication()

    def test_logout_success(self):
        user = User.objects.create_user(
            email="user@test.com",
            username="user",
            password="StrongPass@123",
        )

        refresh = RefreshToken.for_user(user)

        factory = APIRequestFactory()
        request = factory.post(
            "/auth/sign-out/",
            {"refresh": str(refresh)},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}",
        )

        response = SignOutAuthEndpoint.as_view()(request)

        self.assertEqual(response.status_code, 205)
        self.assertEqual(BlacklistedToken.objects.count(), 1)


class TestRefreshTokenAuthentication(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_refresh_token_success(self):
        user = User.objects.create(email="user@test.com")
        user.set_password("StrongPass@123")
        user.save()

        refresh = RefreshToken.for_user(user)

        request = self.factory.post(
            "/auth/refresh-token",
            {"refresh": str(refresh)},
            format="json",
        )

        response = RefreshTokenEndpoint.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_refresh_token_missing(self):
        request = self.factory.post(
            "/auth/refresh-token",
            {},
            format="json",
        )

        response = RefreshTokenEndpoint.as_view()(request)

        self.assertEqual(response.status_code, 400)

    def test_refresh_token_invalid(self):
        request = self.factory.post(
            "/auth/refresh-token",
            {"refresh": "invalid.token.value"},
            format="json",
        )

        response = RefreshTokenEndpoint.as_view()(request)

        self.assertEqual(response.status_code, 400)

    def test_refresh_token_blacklisted(self):
        user = User.objects.create(email="user@test.com")
        user.set_password("StrongPass@123")
        user.save()

        refresh = RefreshToken.for_user(user)
        refresh.blacklist()

        request = self.factory.post(
            "/auth/refresh-token",
            {"refresh": str(refresh)},
            format="json",
        )

        response = RefreshTokenEndpoint.as_view()(request)

        self.assertEqual(response.status_code, 400)

    def test_refresh_token_not_blacklisted_on_success(self):
        user = User.objects.create(email="user@test.com")
        user.set_password("StrongPass@123")
        user.save()

        refresh = RefreshToken.for_user(user)

        request = self.factory.post(
            "/auth/refresh-token",
            {"refresh": str(refresh)},
            format="json",
        )

        RefreshTokenEndpoint.as_view()(request)

        self.assertEqual(BlacklistedToken.objects.count(), 0)
