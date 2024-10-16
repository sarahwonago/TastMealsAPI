import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework import status
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample, inline_serializer

from account.permissions import IsAdmin

from notification.models import Notification
from notification.serializers import NotificationSerializer

from review.models import Review
from review.serializers import ReviewSerializer


# sets up logging for this module
logger = logging.getLogger(__name__)

class CafeadminHomeAPIView(APIView):
    """
    Handles the cafeadmin dashboard endpoint.
    Cafeadmin must be authenticated.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        logger.info(f"Cafeadmin {request.user.username} accessed cafeadmin home.")

        return Response({"message":"Welcome home cafeadmin"}, status=status.HTTP_200_OK)
                 

class ReviewsAPIView(APIView):
    """
    API view to list all reviews made by customers.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class NotificationListView(APIView):
    """
    API view to list all notifications for the authenticated user with filtering, searching, and ordering.

    Query Parameters:
    - is_read (bool, optional): Filter notifications by read/unread status (true/false).
    - search (str, optional): Search notifications by message content.
    - ordering (str, optional): Order by any field, defaults to '-updated_at' (e.g., 'created_at' or '-created_at').

    Responses:
    - 200: Success, list of notifications.
    - 400: Invalid query parameters.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='is_read', description='Filter by read status', required=False, type=bool),
            OpenApiParameter(name='search', description='Search by message content', required=False, type=str),
            OpenApiParameter(name='ordering', description='Order by field, e.g., "-created_at"', required=False, type=str)
        ],
        responses={
            200: NotificationSerializer(many=True),
            400: OpenApiResponse(description="Invalid query parameters.")
        }
    )
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(user=user)
        
        # Filtering by read/unread status
        is_read = request.query_params.get('is_read', None)
        if is_read is not None:
            notifications = notifications.filter(is_read=is_read.lower() == 'true')
        
        # Searching by message
        search_query = request.query_params.get('search', None)
        if search_query:
            notifications = notifications.filter(Q(message__icontains=search_query))
        
        # Ordering by created_at or updated_at
        ordering = request.query_params.get('ordering', '-updated_at')  # Default ordering by most recent
        notifications = notifications.order_by(ordering)

        serializer = NotificationSerializer(notifications, many=True)
        logger.info(f"Listed notifications for user {user.username}.")
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationDetailView(APIView):
    """
    API view to retrieve a single notification and mark it as read.

    URL Parameters:
    - pk (int): Primary key of the notification.

    Responses:
    - 200: Success, notification retrieved and marked as read.
    - 404: Notification not found.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        responses={
            200: NotificationSerializer,
            404: OpenApiResponse(description="Notification not found.")
        }
    )
    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)

        # Mark as read when viewed
        if not notification.is_read:
            notification.is_read = True
            notification.save()
            logger.info(f"Notification {pk} marked as read for user {request.user.username}.")

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Notification deleted."),
            404: OpenApiResponse(description="Notification not found.")
        }
    )
    def delete(self, request, pk):
        """
        Deletes a single notification by its ID.

        URL Parameters:
        - pk (int): Primary key of the notification to be deleted.

        Responses:
        - 204: Success, notification deleted.
        - 404: Notification not found.
        """
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.delete()
        logger.info(f"Notification {pk} deleted for user {request.user.username}.")
        return Response({"detail": "Notification deleted."}, status=status.HTTP_204_NO_CONTENT)


class BulkMarkAsReadView(APIView):
    """
    API view to mark multiple notifications as read.

    Request Body:
    - notification_ids (list of int): List of notification IDs to be marked as read.

    Responses:
    - 200: Success, notifications marked as read.
    - 400: Invalid request body or no notification IDs provided.
    - 404: No matching notifications found.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        request=inline_serializer(
            name="BulkMarkAsReadRequest",
            fields={
                'notification_ids': serializers.ListField(
                    child=serializers.IntegerField(),
                    help_text="List of notification IDs to mark as read."
                )
            }
        ),
        responses={
            200: OpenApiResponse(description="Notifications marked as read."),
            400: OpenApiResponse(description="Invalid request body."),
            404: OpenApiResponse(description="No matching notifications found.")
        }
    )
    def patch(self, request):
        notification_ids = request.data.get('notification_ids', [])
        user = request.user

        if not notification_ids:
            logger.error(f"No notification IDs provided for bulk mark as read by user {user.username}.")
            return Response({"detail": "No notification IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        notifications = Notification.objects.filter(id__in=notification_ids, user=user)
        if not notifications.exists():
            logger.warning(f"No matching notifications found for bulk mark as read by user {user.username}.")
            return Response({"detail": "No matching notifications found."}, status=status.HTTP_404_NOT_FOUND)

        notifications.update(is_read=True)
        logger.info(f"Marked notifications {notification_ids} as read for user {user.username}.")
        return Response({"detail": "Notifications marked as read."}, status=status.HTTP_200_OK)

