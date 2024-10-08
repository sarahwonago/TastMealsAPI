from django.urls import path

from .views import (
    CustomerHomeAPIView, CategoryListCreateAPIView, CategoryDetailAPIView,
    DiningTableListAPIView, SpecialOfferListAPIView, AddItemToCartAPIView, CartAPIView,
    CartItemDetailAPIView
)


urlpatterns = [
    # home
    path("", CustomerHomeAPIView.as_view(), name="customer-home"),

    # categories with fooditems endpoints
    path("categories/", CategoryListCreateAPIView.as_view(), name="customer-categories-list-create"),
    path("categories/<uuid:pk>/fooditems/", CategoryDetailAPIView.as_view(), name="customer-category-detail"),

    # dinning tables endpoint
    path("dinning-tables/", DiningTableListAPIView.as_view(), name="customer-dinning"),

    # specialoffer endpoint
    path("specialoffers/", SpecialOfferListAPIView.as_view(), name="customer-specialoffers-list"),

    # Adding items to cart, viewing cart
    path("add-to-cart/<uuid:fooditem_id>/", AddItemToCartAPIView.as_view(), name="customer-add-to-cart"),
    path("my-cart/", CartAPIView.as_view(), name="customer-cart"),

    # Update/Delete specific cart item (using cartitem_id in the URL)
    path('my-cart/<uuid:cartitem_id>/', CartItemDetailAPIView.as_view(), name='cart-item-detail'),
 
]
