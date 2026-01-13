import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import pytz


from .assets import FileAsset
from ..mixins import TimeAuditModel
from .base import BaseModel


class User(AbstractUser, TimeAuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    username = models.CharField(max_length=150, blank=True, null=True, unique=False)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=255)

    avatar = models.TextField(blank=True, null=True)
    avatar_asset = models.ForeignKey(
        FileAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_avatar",
    )

    cover_image = models.URLField(blank=True, null=True, max_length=800)
    cover_image_asset = models.ForeignKey(
        FileAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_cover_images",
    )

    user_timezone = models.CharField(max_length=50, default="UTC")

    last_login_medium = models.CharField(max_length=255, null=True, blank=True)
    last_login_ip = models.CharField(max_length=255, null=True, blank=True)
    last_login_uagent = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"<{self.email}>"


class OrganizerProfile(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="organizer_profile"
    )


class EventMember(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="event_member"
    )
