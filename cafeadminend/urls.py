from django.urls import path

from .views import (CafeadminHomeAPIView, CategoryListCreateAPIView, CategoryDetailAPIView,
                    DiningTableListAPIView, DiningTableDetailAPIView, FoodItemListView, FoodItemDetailView,
                   )


urlpatterns = [
    # home
    path("", CafeadminHomeAPIView.as_view(), name="cafeadmin-home"),
    
    # endpoint for managing categories
    path("categories/", CategoryListCreateAPIView.as_view(), name="categories-list-create"),
    path("categories/<uuid:pk>/", CategoryDetailAPIView.as_view(), name="category-detail"),
    
    # endpoint for managing fooditems under specific categories
    path('categories/<uuid:category_id>/fooditems/', FoodItemListView.as_view(), name='fooditem-list'),
    path('categories/<uuid:category_id>/fooditems/<uuid:fooditem_id>/', FoodItemDetailView.as_view(), name='fooditem-detail'),

    # endpoint for managing dinning tables
    path("dinning-tables/", DiningTableListAPIView.as_view(), name="dinning-list-create"),
    path("dinning-tables/<uuid:pk>/", DiningTableDetailAPIView.as_view(), name="dinning-detail"),

 
   
]
