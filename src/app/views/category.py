from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app.serializers import CategorySerializer
from db.models import EventCategory
from utils.pagination import CustomLimitPagination


class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    pagination_class = CustomLimitPagination
    serializer_class = CategorySerializer

    def list(self, request):
        filters = {}

        category_id = request.query_params.get("id")
        if category_id is not None:
            filters["id"] = category_id

        name = request.query_params.get("name")
        search = request.query_params.get("search")

        q_object = Q()
        if name is not None:
            q_object &= Q(name__icontains=name)

        if search:
            q_object &= Q(name__icontains=search) | Q(description__icontains=search)

        queryset = EventCategory.objects.filter(**filters)

        if q_object:
            queryset = queryset.filter(q_object)

        queryset = queryset.only("id", "name", "description", "slug")

        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return Response(
            {**self.paginator.get_pagination_details(), "result": serializer.data}
        )
