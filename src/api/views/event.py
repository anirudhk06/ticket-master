from datetime import timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from api.filters.event import EventMasterFilter
from api.serializers.event import (
    EventCategorySerializer,
    EventDetailsSerializer,
    EventMasterListSerializer,
    EventTicketListSerializer,
)
from db.models.event import EventCategory, EventMaster, TicketMaster
from utils.pagination import CustomLimitPagination


# Event Category
class EventCategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomLimitPagination
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        paginated_qs = self.paginate_queryset(qs)
        serializer = self.get_serializer(paginated_qs, many=True)
        return self.get_paginated_response(serializer.data)


class EventCategoryDestroyAPI(generics.DestroyAPIView):
    queryset = EventCategory.objects.all()
    permission_classes = [IsAuthenticated]


# Events


class NearestWeekEndEventListPI(generics.ListAPIView):
    serializer_class = EventMasterListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return EventMaster.objects.select_related("category")

    def list(self, request, *args, **kwargs):
        now = timezone.now()
        fields = [
            "id",
            "title",
            "venue",
            "start_at",
            "end_at",
            "is_featured",
            "status",
            "category__id",
            "category__name",
            "category__emoji",
        ]

        nearest_qs = (
            self.get_queryset()
            .filter(start_at__gte=now)
            .values(*fields)
            .order_by("start_at")
        )[:3]

        weekday = now.weekday()
        monday = (now - timedelta(days=weekday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        sunday_end = monday + timedelta(days=6, hours=23, minutes=59, seconds=59)

        weekend_qs = (
            self.get_queryset()
            .filter(start_at__gte=monday, start_at__lte=sunday_end)
            .values(*fields)
            .order_by("start_at")[:3]
        )

        nearest_serializer = self.get_serializer(nearest_qs, many=True)
        weekend_serializer = self.get_serializer(weekend_qs, many=True)

        return Response(
            {"nearest": nearest_serializer.data, "weekend": weekend_serializer.data}
        )


class EventListCreateAPI(generics.ListCreateAPIView):
    serializer_class = EventMasterListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomLimitPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["title"]
    filterset_class = EventMasterFilter

    def get_queryset(self):
        return EventMaster.objects.values(
            "id",
            "title",
            "venue",
            "start_at",
            "end_at",
            "is_featured",
            "status",
            "category__id",
            "category__name",
            "category__emoji",
        ).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        paginated_qs = self.paginate_queryset(qs)
        serializer = self.get_serializer(paginated_qs, many=True)
        return self.get_paginated_response(serializer.data)


class EventRetriveUpdateDestroyAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventMaster.objects.select_related(
        "category", "created_by", "updated_by"
    ).all()
    serializer_class = EventDetailsSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class TicketListCreateAPI(generics.ListCreateAPIView):
    pagination_class = CustomLimitPagination
    serializer_class = EventTicketListSerializer

    def get_queryset(self):
        return (
            TicketMaster.objects.select_related("event")
            .filter(event_id=self.kwargs["event_id"])
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        paginated_qs = self.paginate_queryset(qs)
        serializer = self.get_serializer(paginated_qs, many=True)
        return self.get_paginated_response(serializer.data)
