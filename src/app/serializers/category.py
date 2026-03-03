from rest_framework import serializers

from db.models import EventCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ["id", "name", "description", "slug", "emoji"]
