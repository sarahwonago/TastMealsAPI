from django.urls import path

from .views import (
    CustomerHomeAPIView, CategoryListAPIView, CategoryDetailAPIView, FoodItemListAPIView,
    DiningTableListAPIView, SpecialOfferListAPIView,NotificationListView, 
    NotificationDetailView, BulkDeleteNotificationsView, BulkMarkAsReadView, CustomerLoyaltyPointView, RedeemLoyaltyPointsAPIView, RedemptionOptionListView
)


urlpatterns = [
    # home
    path("", CustomerHomeAPIView.as_view(), name="customer-home"),

    # categories with fooditems endpoints
    path("categories/", CategoryListAPIView.as_view(), name="customer-categories-list-create"),
    path("categories/<uuid:pk>/fooditems/", CategoryDetailAPIView.as_view(), name="customer-category-detail"),

    # all fooditems endpoint
    path("fooditems/", FoodItemListAPIView.as_view(), name="customer-fooditems"),

    # dinning tables endpoint
    path("dinning-tables/", DiningTableListAPIView.as_view(), name="customer-dinning"),

    # specialoffer endpoint
    path("specialoffers/", SpecialOfferListAPIView.as_view(), name="customer-specialoffers-list"),

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
    path("loyalty-points/<uuid:redemption_id>/redeem/", RedeemLoyaltyPointsAPIView.as_view(), name="customer-redeem-points"),

    # redemption options
    path("redemption-options/", RedemptionOptionListView.as_view(), name="customer-remption-option"),
]
