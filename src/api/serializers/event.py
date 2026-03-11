from rest_framework import serializers

from db.models import EventCategory, EventMaster


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ["id", "name", "description", "emoji", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class EventMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMaster
        fields = [
            "id",
            "title",
            "description",
            "venue",
            "start_at",
            "end_at",
            "sale_start_at",
            "total_capacity",
            "is_featured",
            "status",
            "category",
            "meta",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
