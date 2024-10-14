from django.urls import path

from .views import (CafeadminHomeAPIView, ReviewsAPIView, NotificationListView, NotificationDetailView, BulkDeleteNotificationsView, BulkMarkAsReadView,
                    RedemptionOptionDetailView,RedemptionOptionListCreateView,RedemptionTransactionDetailView, RedemptionTransactionListView, MarkRedemptionTransactionDeliveredView
                   )


urlpatterns = [
    # home
    path("", CafeadminHomeAPIView.as_view(), name="cafeadmin-home"),
    
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

