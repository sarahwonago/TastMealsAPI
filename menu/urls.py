from django.urls import path

from .views import (CategoryListCreateAPIView, CategoryDetailAPIView, )


urlpatterns = [
  
    # endpoint for managing categories
    path("categories/", CategoryListCreateAPIView.as_view(), name="categories-list-create"),
    path("categories/<uuid:pk>/", CategoryDetailAPIView.as_view(), name="category-detail"),
    
]

