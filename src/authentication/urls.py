from django.urls import path

from .views import (
    SignInAuthEndpoint,
    SignOutAuthEndpoint,
    SignUpAuthEndpoint,
)

urlpatterns = [
    # Credentials
    path("sign-in", SignInAuthEndpoint.as_view(), name="sign-in"),
    path("sign-up", SignUpAuthEndpoint.as_view(), name="sign-up"),
    path("sign-out", SignOutAuthEndpoint.as_view(), name="sign-out"),
]
