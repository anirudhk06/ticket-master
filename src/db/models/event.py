from django.db import models
from django.utils.text import slugify

from .base import BaseModel


class EventCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    emoji = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Event Category"
        verbose_name_plural = "Event Categories"
        ordering = ("-created_at",)


class EventMaster(BaseModel):
    class EventStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    title = models.CharField(max_length=255)
    description = models.TextField()
    venue = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    start_at = models.DateTimeField(auto_now_add=True)
    end_at = models.DateTimeField(null=True, blank=True)
    sale_start_at = models.DateTimeField(null=True, blank=True)
    total_capacity = models.PositiveIntegerField(default=0)

    is_featured = models.BooleanField(default=False)

    status = models.CharField(
        max_length=100, choices=EventStatus.choices, default=EventStatus.DRAFT
    )

    category = models.ForeignKey(
        EventCategory, on_delete=models.CASCADE, related_name="events"
    )
    meta = models.JSONField(default=dict)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Event Master"
        verbose_name_plural = "Event Masters"


class TicketMaster(BaseModel):
    event = models.ForeignKey(
        EventMaster, on_delete=models.CASCADE, related_name="tickets"
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.event.title}"

    class Meta:
        verbose_name = "Ticket Master"
        verbose_name_plural = "Ticket Masters"
