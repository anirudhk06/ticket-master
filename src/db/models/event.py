from django.db import models

from .base import BaseModel


class EventCategory(BaseModel):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    description = models.TextField(blank=True, default="")
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Event Category"
        verbose_name_plural = "Event Categories"

    def __str__(self) -> str:
        return self.name


class EventMaster(BaseModel):
    name = models.CharField(max_length=255, db_index=True)

    description = models.TextField(blank=True, default="")

    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)

    venue_name = models.CharField(max_length=255, blank=True, default="")
    venue_address = models.TextField(blank=True, default="")

    capacity = models.PositiveIntegerField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self) -> str:
        return self.name
