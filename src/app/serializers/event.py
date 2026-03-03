from rest_framework import serializers

from db.models import Asset, EventCategory, EventMaster, EventTicket


class NearestWeekendEventsSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    start_at = serializers.DateTimeField()
    category__name = serializers.CharField()
    category__emoji = serializers.CharField()
    starting_from = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True
    )
    bg_color = serializers.CharField()
    venue_name = serializers.CharField()
    total_quantity = serializers.IntegerField()
