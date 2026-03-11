from django.db import models
from django.db.models import manager
from django.utils import timezone


class TimeAuditModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        abstract = True


class UserAuditModel(models.Model):
    created_by = models.ForeignKey(
        "db.User",
        on_delete=models.SET_NULL,
        related_name="%(class)s_created_by",
        verbose_name="Created By",
        null=True,
    )
    updated_by = models.ForeignKey(
        "db.User",
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated_by",
        verbose_name="Updated By",
        null=True,
    )

    class Meta:
        abstract = True


class AuditModel(TimeAuditModel, UserAuditModel):
    """To path when the record was created and last modified"""

    class Meta:
        abstract = True
