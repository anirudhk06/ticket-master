from django.urls import path

from .views import (
    SignInAuthEndpoint,
    SignUpAuthEndpoint,
)

urlpatterns = [
    path("sign-in/", SignInAuthEndpoint.as_view(), name="sign-in"),
    path("sign-up/", SignUpAuthEndpoint.as_view(), name="sign-up"),
]
