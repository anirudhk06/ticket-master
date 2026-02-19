from django.urls import path

from .views import (
    ChangePasswordEndpoint,
    CSRFTokenEndpoint,
    GoogleOauthCallbackEndpoint,
    GoogleOauthInitiateEndpoint,
    RefreshTokenEndpoint,
    SignInAuthEndpoint,
    SignOutAuthEndpoint,
    SignUpAuthEndpoint,
)

urlpatterns = [
    path("sign-out", SignOutAuthEndpoint.as_view(), name="sign-out"),
    # email
    path("sign-in", SignInAuthEndpoint.as_view(), name="sign-in"),
    path("sign-up", SignUpAuthEndpoint.as_view(), name="sign-up"),
    path("refresh-token", RefreshTokenEndpoint.as_view(), name="refresh-token"),
    # password
    path("change-password", ChangePasswordEndpoint.as_view(), name="change-password"),
    # csrf
    path("csrf-token", CSRFTokenEndpoint.as_view(), name="get-csrf-token"),
    # google
    path("google/initiate", GoogleOauthInitiateEndpoint.as_view(), name="google-initiate"),
    path("google/callback", GoogleOauthCallbackEndpoint.as_view(), name="google-callback"),
]