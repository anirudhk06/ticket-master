from django.urls import path

from app.views import (
    EventListCreateAPI,
    FeaturedEventsAPI,
    NearestWeekendEventsAPI,
)

urlpatterns = [
    path("events", EventListCreateAPI.as_view(), name="event-list-create"),
    path(
        "events/featured",
        FeaturedEventsAPI.as_view(),
        name="event-featured",
    ),
    path(
        "events/nearest-weekend",
        NearestWeekendEventsAPI.as_view(),
        name="event-nearest-weekend",
    ),
]
