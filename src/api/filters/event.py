from django_filters import rest_framework as filters

from db.models.event import EventMaster


class EventMasterFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    ordering = filters.OrderingFilter(
        fields=(("created_at", "created_at"), ("start_at", "start_at")),
        field_labels={
            "created_at": "Created At",
            "start_at": "Start At",
        },
    )

    class Meta:
        model = EventMaster
        fields = ["title", "ordering"]
