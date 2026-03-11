from django.urls import path

from api.views import EventCategoryDestroyAPI, EventCategoryListCreateAPIView

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
]
