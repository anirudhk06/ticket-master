from django.db import models

from .base import BaseModel


class Asset(BaseModel):
    class AssetType(models.TextChoices):
        IMAGE = "IMAGE", "Image"
        VIDEO = "VIDEO", "Video"
        DOCUMENT = "DOCUMENT", "Document"

    name = models.CharField(max_length=255, blank=True, default="")
    file = models.FileField(upload_to="assets/")
    asset_type = models.CharField(
        max_length=20, choices=AssetType.choices, default=AssetType.IMAGE
    )
    alt_text = models.CharField(max_length=255, blank=True, default="")
    mime_type = models.CharField(max_length=100, blank=True, default="")
    size = models.PositiveIntegerField(
        help_text="File size in bytes", null=True, blank=True
    )

    class Meta:
        verbose_name = "Asset"
        verbose_name_plural = "Assets"

    def __str__(self) -> str:
        return self.name or str(self.file.name)
