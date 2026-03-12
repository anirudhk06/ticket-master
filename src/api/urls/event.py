from django.urls import path

from api.views import (
    EventCategoryDestroyAPI,
    EventCategoryListCreateAPIView,
    EventListCreateAPI,
    EventRetriveUpdateDestroyAPI,
    NearestWeekEndEventListPI,
    TicketListCreateAPI,
)

urlpatterns = [
    path(
        "event/categories",
        EventCategoryListCreateAPIView.as_view(),
        name="event-category-list-create",
    ),
    path(
        "event/category/<uuid:pk>",
        EventCategoryDestroyAPI.as_view(),
        name="event-category-destroy",
    ),
    path(
        "events",
        EventListCreateAPI.as_view(),
        name="event-list-create",
    ),
    path(
        "events/<uuid:pk>",
        EventRetriveUpdateDestroyAPI.as_view(),
        name="event-retrieve-update-destroy",
    ),
    path(
        "events/nearest-weekend",
        NearestWeekEndEventListPI.as_view(),
        name="event-nearest-weekend",
    ),
    path(
        "event/<uuid:event_id>/tickets",
        TicketListCreateAPI.as_view(),
        name="ticket-list-create",
    ),
]
