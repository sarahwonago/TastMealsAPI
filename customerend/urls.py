from django.urls import path

from .views import (
    CustomerHomeAPIView, CategoryListCreateAPIView, CategoryDetailAPIView,
    DiningTableListAPIView, SpecialOfferListAPIView, AddItemToCartAPIView, CartAPIView,
    CartItemDetailAPIView, PlaceOrderView, OrderListView, CancelOrderView, PaymentView,
    AddReviewView, UpdateReviewView, UserReviewsView, DeleteReviewView, NotificationListView, 
    NotificationDetailView, BulkDeleteNotificationsView, BulkMarkAsReadView, CustomerLoyaltyPointView, RedeemLoyaltyPointsAPIView, RedemptionOptionListView
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
    path('my-cart/<uuid:cartitem_id>/', CartItemDetailAPIView.as_view(), name='customer-cart-item-detail'),

    # placing an order endpoint, listing all orders, cancelling unpaid orders
    path('my-cart/place-order/', PlaceOrderView.as_view(), name='customer-place-order'),
    path('orders/', OrderListView.as_view(), name='customer-orders'),
    path('orders/<uuid:order_id>/cancel/', CancelOrderView.as_view(), name='customer-cancel-order'),

    # payment for order
    path('order/<uuid:order_id>/payment/', PaymentView.as_view(), name="customer-pay"),

    # endpoints for reviews
    path('orders/<uuid:order_id>/review/', AddReviewView.as_view(), name='customer-add-review'),
    path('reviews/', UserReviewsView.as_view(), name='customer-reviews'),
    path('reviews/<uuid:review_id>/update/', UpdateReviewView.as_view(), name='customer-update-review'),
    path('reviews/<uuid:review_id>/delete/', DeleteReviewView.as_view(), name='customer-delete-review'),

    # List notifications, filtering, searching, ordering
    path('notifications/', NotificationListView.as_view(), name='customer-notifications-list'),

    # Mark as read, bulk delete
    path('notifications/mark-as-read/', BulkMarkAsReadView.as_view(), name='customer-bulk-mark-as-read'),
    path('notifications/delete/', BulkDeleteNotificationsView.as_view(), name='customer-bulk-delete-notifications'),

    # View a single notification and mark it as read
    path('notifications/<uuid:pk>/', NotificationDetailView.as_view(), name='customer-notification-detail'),

    # endpoint to view customer points
    path("loyalty-points/", CustomerLoyaltyPointView.as_view(), name="customer-loyalty-points"),

    # endpoint to redeem loyalty point
    path("loyalty-points/redeem/<uuid:redemption_id>/", RedeemLoyaltyPointsAPIView.as_view(), name="customer-redeem-points"),

    # redemption options
    path("redemption-options/", RedemptionOptionListView.as_view(), name="customer-remption-option"),
]
