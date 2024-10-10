from django.urls import path

from .views import (CafeadminHomeAPIView, CategoryListCreateAPIView, CategoryDetailAPIView,
                    DiningTableListAPIView, DiningTableDetailAPIView, FoodItemListView, FoodItemDetailView,SpecialOfferCreateAPIView, SpecialOfferDetailAPIView, SpecialOfferListAPIView, ReviewsAPIView, NotificationListView, NotificationDetailView, BulkDeleteNotificationsView, BulkMarkAsReadView,
                    RedemptionOptionDetailView,RedemptionOptionListCreateView,RedemptionTransactionDetailView, RedemptionTransactionListView, MarkRedemptionTransactionDeliveredView
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

    # specialoffer endpoints
    path("specialoffers/", SpecialOfferListAPIView.as_view(), name='specialoffer-list'),
    path('specialoffers/<uuid:fooditem_id>/', SpecialOfferCreateAPIView.as_view(), name='specialoffer-create'),
    path('specialoffers/<uuid:offer_id>/detail/', SpecialOfferDetailAPIView.as_view(), name='specialoffer-detail'),

    # admin viewing reviews made by customers
    path("customer-reviews/", ReviewsAPIView.as_view(), name="reviews"),

    # List notifications, filtering, searching, ordering
    path('notifications/', NotificationListView.as_view(), name='notifications-list'),

    # Mark as read, bulk delete
    path('notifications/mark-as-read/', BulkMarkAsReadView.as_view(), name='bulk-mark-as-read'),
    path('notifications/delete/', BulkDeleteNotificationsView.as_view(), name='bulk-delete-notifications'),

    # View a single notification and mark it as read
    path('notifications/<uuid:pk>/', NotificationDetailView.as_view(), name='notification-detail'),

    # redemption option endpoints
    path('redemption-options/', RedemptionOptionListCreateView.as_view(), name='redemption-options'),
    path('redemption-options/<uuid:pk>/', RedemptionOptionDetailView.as_view(), name='redemption-option-detail'),

    # redemption option transaction endpoints
    path('redemption-transactions/', RedemptionTransactionListView.as_view(), name='redemption-transactions'),
    path('redemption-transactions/<uuid:pk>/', RedemptionTransactionDetailView.as_view(), name='redemption-transaction-detail'),
    path('redemption-transactions/<uuid:pk>/mark-delivered/', MarkRedemptionTransactionDeliveredView.as_view(), name='redemption-transaction-delivered'),

]
