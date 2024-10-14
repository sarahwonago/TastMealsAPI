from django.urls import path
from .views import CancelOrderView, PlaceOrderView, OrderListView

urlpatterns = [
     # placing an order endpoint, listing all orders, cancelling unpaid orders
    path('my-cart/place-order/', PlaceOrderView.as_view(), name='customer-place-order'),
    path('orders/', OrderListView.as_view(), name='customer-orders'),
    path('orders/<uuid:order_id>/cancel/', CancelOrderView.as_view(), name='customer-cancel-order'),
]