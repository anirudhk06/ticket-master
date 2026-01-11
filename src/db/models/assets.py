from uuid import uuid4

from django.db import models

from .base import BaseModel


def get_upload_path(instance, filename) -> str:
    return f"user-{uuid4().hex}-{filename}"


class FileAsset(BaseModel):
    user = models.ForeignKey(
        "db.User", on_delete=models.CASCADE, null=True, related_name="assets"
    )
    asset = models.FileField(upload_to=get_upload_path, max_length=800)
    entity_type = models.CharField(max_length=255, null=True, blank=True)
    attributes = models.JSONField(default=dict)
    size = models.FloatField(default=0)
    storage_metaclass = models.JSONField(default=dict)

    class Meta:
        verbose_name = "File Asset"
        verbose_name_plural = "File Assets"
        db_table = "file_assets"
        ordering = ("-created_at",)

    def __str__(self):
        return str(self.asset)
