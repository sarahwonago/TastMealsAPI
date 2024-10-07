from django.urls import path

from .views import (
    CustomerHomeAPIView, CategoryListCreateAPIView, CategoryDetailAPIView,
    DiningTableListAPIView
)


urlpatterns = [
    path("", CustomerHomeAPIView.as_view(), name="customer-home"),
    path("categories/", CategoryListCreateAPIView.as_view(), name="customer-categories-list-create"),
    path("categories/<uuid:pk>/", CategoryDetailAPIView.as_view(), name="customer-category-detail"),
    path("dinning-tables/", DiningTableListAPIView.as_view(), name="customer-dinning"),
 
]
