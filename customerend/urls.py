from django.urls import path

from .views import (
    CustomerHomeAPIView, CategoryListCreateAPIView, CategoryDetailAPIView,
    DiningTableListAPIView
)


urlpatterns = [
    # home
    path("", CustomerHomeAPIView.as_view(), name="customer-home"),

    # categories with fooditems endpoints
    path("categories/", CategoryListCreateAPIView.as_view(), name="customer-categories-list-create"),
    path("categories/<uuid:pk>/fooditems/", CategoryDetailAPIView.as_view(), name="customer-category-detail"),

    # dinning tables endpoint
    path("dinning-tables/", DiningTableListAPIView.as_view(), name="customer-dinning"),
 
]
