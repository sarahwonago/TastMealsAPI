from django.urls import path

from .views import (CafeadminHomeAPIView, CategoryListCreateAPIView, CategoryDetailAPIView)


urlpatterns = [
    path("", CafeadminHomeAPIView.as_view(), name="cafeadmin-home"),
    path("categories/", CategoryListCreateAPIView.as_view(), name="categories-list-create"),
    path("categories/<uuid:pk>/", CategoryDetailAPIView.as_view(), name="category-detail"),
 
]
