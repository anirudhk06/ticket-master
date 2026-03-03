from django.db import models

from .assets import Asset
from .base import BaseModel


class EventTag(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Event Tag"
        verbose_name_plural = "Event Tags"

    def __str__(self) -> str:
        return self.name


class EventCategory(BaseModel):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    emoji = models.CharField(max_length=10, null=True, blank=True, default="🎪")
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

    main_image = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_banner_images",
    )

    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)

    venue_name = models.CharField(max_length=255, blank=True, default="")
    venue_address = models.TextField(blank=True, default="")

    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    bg_color = models.TextField(null=True, blank=True)
    highlights = models.TextField(null=True, blank=True)

    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    tags = models.ManyToManyField(
        EventTag,
        blank=True,
        related_name="events",
    )

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self) -> str:
        return self.name


class EventAsset(BaseModel):
    event = models.ForeignKey(
        EventMaster, on_delete=models.CASCADE, related_name="additional_assets"
    )
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="event_assets_rel"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Event Asset"
        verbose_name_plural = "Event Assets"
        ordering = ["order"]

    def __str__(self) -> str:
        return f"Asset for {self.event.name}"


class EventTicket(BaseModel):
    class TicketType(models.TextChoices):
        FREE = "FREE", "Free"
        PAID = "PAID", "Paid"

    cover_image = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_ticket_cover_images",
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(
        max_length=3,
        choices=[("INR", "Indian Rupee"), ("USD", "US Dollar"), ("EUR", "Euro")],
        default="INR",
    )
    quantity = models.PositiveIntegerField(
        null=True, blank=True, help_text="Total tickets available"
    )
    available_quantity = models.PositiveIntegerField(
        null=True, blank=True, help_text="Currently available"
    )

    price_type = models.CharField(
        max_length=20, choices=TicketType.choices, default=TicketType.PAID
    )

    event = models.ForeignKey(
        EventMaster,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    is_active = models.BooleanField(default=True)
    sales_start_at = models.DateTimeField(null=True, blank=True)
    sales_end_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Event Ticket"
        verbose_name_plural = "Event Tickets"
        unique_together = ("event", "name")

    def __str__(self) -> str:
        return f"{self.name} - {self.event.name}"
