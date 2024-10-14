from django.urls import path

from .views import (
  AddItemToCartAPIView, CartAPIView,
    CartItemDetailAPIView, 
)


urlpatterns = [
    
    # Adding items to cart, viewing cart
    path("add-to-cart/<uuid:fooditem_id>/", AddItemToCartAPIView.as_view(), name="customer-add-to-cart"),
    path("my-cart/", CartAPIView.as_view(), name="customer-cart"),

    # Update/Delete specific cart item (using cartitem_id in the URL)
    path('my-cart/<uuid:cartitem_id>/', CartItemDetailAPIView.as_view(), name='customer-cart-item-detail'),

]
