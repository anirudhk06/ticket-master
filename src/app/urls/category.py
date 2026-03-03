from django.urls import path

from app.views import CategoryListView

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
]
