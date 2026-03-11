from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from api.serializers.event import EventCategorySerializer
from db.models.event import EventCategory
from utils.pagination import CustomLimitPagination


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
