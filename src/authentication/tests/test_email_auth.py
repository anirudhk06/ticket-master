from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.views.email import SignUpAuthEndpoint
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
