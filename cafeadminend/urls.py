from django.urls import path

from .views import (CafeadminHomeAPIView, ReviewsAPIView, NotificationListView, NotificationDetailView, BulkMarkAsReadView
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


    # View a single notification and mark it as read
    path('notifications/<uuid:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
]

