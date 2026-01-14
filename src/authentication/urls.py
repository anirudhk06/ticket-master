from django.urls import path

from .views import (
    SignInAuthEndpoint,
    SignOutAuthEndpoint,
    SignUpAuthEndpoint,
    RefreshTokenEndpoint
)

urlpatterns = [
    # Credentials
    path("sign-in", SignInAuthEndpoint.as_view(), name="sign-in"),
    path("sign-up", SignUpAuthEndpoint.as_view(), name="sign-up"),
    path("refresh-token", RefreshTokenEndpoint.as_view(), name="refresh-token"),
    path("sign-out", SignOutAuthEndpoint.as_view(), name="sign-out"),
]
