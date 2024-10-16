from django.urls import path

from .views import (CategoryListCreateAPIView, CategoryDetailAPIView, FoodItemListView, FoodItemDetailView,SpecialOfferCreateAPIView, SpecialOfferDetailAPIView, SpecialOfferListAPIView,)


urlpatterns = [
  
    # endpoint for managing categories
    path("categories/", CategoryListCreateAPIView.as_view(), name="categories-list-create"),
    path("categories/<uuid:pk>/", CategoryDetailAPIView.as_view(), name="category-detail"),

    # endpoint for managing fooditems under specific categories
    path('categories/<uuid:category_id>/fooditems/', FoodItemListView.as_view(), name='fooditem-list'),
    path('categories/<uuid:category_id>/fooditems/<uuid:fooditem_id>/', FoodItemDetailView.as_view(), name='fooditem-detail'),

    # specialoffer endpoints
    path("specialoffers/", SpecialOfferListAPIView.as_view(), name='specialoffer-list'),
    path('specialoffers/<uuid:fooditem_id>/', SpecialOfferCreateAPIView.as_view(), name='specialoffer-create'),
    path('specialoffers/<uuid:offer_id>/detail/', SpecialOfferDetailAPIView.as_view(), name='specialoffer-detail'),
]

