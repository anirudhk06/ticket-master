from datetime import timedelta

from django.db.models import DecimalField, Min, Sum
from django.db.models.functions import Cast, Coalesce
from django.utils import timezone
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app.serializers import NearestWeekendEventsSerializer
from db.models import EventMaster
from utils.pagination import CustomLimitPagination


class NearestWeekendEventsAPI(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = NearestWeekendEventsSerializer

    def get_queryset(self):
        return (
            EventMaster.objects.filter(
                is_published=True, start_at__date__gte=timezone.now().date()
            )
            .annotate(
                starting_from=Min("tickets__price"),
                total_quantity=Coalesce(Sum("tickets__quantity"), 0),
            )
            .select_related("category")
        ).values(
            "id",
            "name",
            "description",
            "venue_name",
            "bg_color",
            "start_at",
            "category__name",
            "category__emoji",
            "starting_from",
            "total_quantity",
        )

    def list(self, request):
        base_queryset = self.get_queryset()

        nearest_events = base_queryset.order_by("start_at")[:3]
        now = timezone.localtime()
        weekday = now.weekday()

        days_until_saturday = (5 - weekday) % 7
        weekend_start = (now + timedelta(days=days_until_saturday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        weekend_end = (weekend_start + timedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        this_weekend_events = base_queryset.filter(
            start_at__range=(weekend_start, weekend_end)
        ).order_by("start_at")[:3]

        return Response(
            {
                "nearest": self.get_serializer(nearest_events, many=True).data,
                "weekend": self.get_serializer(this_weekend_events, many=True).data,
            }
        )


class FeaturedEventsAPI(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        event = (
            EventMaster.objects.filter(is_featured=True, is_published=True)
            .annotate(
                total_quantity=Coalesce(Sum("tickets__quantity"), 0),
                starting_from=Min("tickets__price"),
            )
            .order_by("-start_at")
            .values(
                "id",
                "name",
                "description",
                "venue_name",
                "bg_color",
                "start_at",
                "category__name",
                "category__emoji",
                "starting_from",
                "total_quantity",
            )
            .first()
        )

        if not event:
            return Response(
                {"message": "No featured event found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(event)


class EventListCreateAPI(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = None
    queryset = EventMaster.objects.all()
