from django.urls import path

from .views import (CafeadminHomeAPIView, CategoryListCreateAPIView, CategoryDetailAPIView,
                    DiningTableListAPIView, DiningTableDetailAPIView, FoodItemListView, FoodItemDetailView
                    )


urlpatterns = [
    path("", CafeadminHomeAPIView.as_view(), name="cafeadmin-home"),
    
    path("categories/", CategoryListCreateAPIView.as_view(), name="categories-list-create"),
    path("categories/<uuid:pk>/", CategoryDetailAPIView.as_view(), name="category-detail"),
    

    path('categories/<uuid:category_id>/fooditems/', FoodItemListView.as_view(), name='fooditem-list'),
    path('categories/<uuid:category_id>/fooditems/<uuid:fooditem_id>/', FoodItemDetailView.as_view(), name='fooditem-detail'),


    path("dinning-tables/", DiningTableListAPIView.as_view(), name="dinning-list-create"),
    path("dinning-tables/<uuid:pk>/", DiningTableDetailAPIView.as_view(), name="dinning-detail"),
 
]
