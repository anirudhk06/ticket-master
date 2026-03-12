from rest_framework import serializers

from db.models import EventCategory, EventMaster, TicketMaster


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ["id", "name", "description", "emoji", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class EventMasterListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    venue = serializers.CharField()
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    is_featured = serializers.BooleanField()
    status = serializers.CharField()

    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        return {
            "id": obj["category__id"],
            "name": obj["category__name"],
            "emoji": obj["category__emoji"],
        }


class EventDetailsSerializer(serializers.ModelSerializer):
    class CategorySerializer(serializers.ModelSerializer):
        class Meta:
            model = EventCategory
            fields = ["id", "name", "description", "emoji"]

    category = CategorySerializer(read_only=True)

    class Meta:
        model = EventMaster
        fields = "__all__"


class EventTicketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMaster
        fields = ["id", "name", "price", "quantity", "is_active", "event"]
