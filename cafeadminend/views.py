import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework import status
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample, inline_serializer
from drf_spectacular.types import OpenApiTypes

from account.permissions import IsAdmin

from notification.models import Notification
from notification.serializers import NotificationSerializer

from review.models import Review
from review.serializers import ReviewSerializer

from order.models import Order
from order.serializers import OrderSerializer

from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Count, Sum
from rewards.models import RedemptionTransaction


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


class CafeAdminOrderListView(APIView):
    """
    Handles the listing of all orders for cafe admin with filtering, searching, and ordering.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='status', description='Filter by order status', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='search', description='Search by customer name', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='ordering', description='Order by a specific field like created_at', required=False, type=OpenApiTypes.STR)
        ],
        responses={200: OrderSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        """
        Fetch all orders with optional filtering, search, and ordering.
        """
        orders = Order.objects.filter(is_paid=True)

        # Filtering by status
        status_filter = request.query_params.get('status', None)
        if status_filter:
            orders = orders.filter(status=status_filter)

        # Searching by customer name 
        search_query = request.query_params.get('search', None)
        if search_query:
            orders = orders.filter(
                Q(user__username__icontains=search_query) 
            ).distinct()

        # Ordering by fields (default by creation date descending)
        ordering = request.query_params.get('ordering', '-created_at')
        orders = orders.order_by(ordering)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarkOrderCompleteAPIView(APIView):
    """
    Endpoint for cafe admin to mark an order as complete.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Order marked as complete."),
            404: OpenApiResponse(description="Order not found.")
        }
    )
    def patch(self, request, order_id, *args, **kwargs):
        """
        Marks a specific order as complete.
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.status == 'COMPLETE':
            return Response({"detail": "Order is already marked as complete."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'COMPLETE'
        order.save()

        return Response({"detail": "Order marked as complete."}, status=status.HTTP_200_OK)
    


class AdminAnalyticsView(APIView):
    """
    Endpoint to provide analytics for the admin.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Analytics data retrieved successfully."),
            400: OpenApiResponse(description="Error in retrieving analytics data.")
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Get analytics data for the admin.
        """

        # Total Orders
        total_orders = Order.objects.filter(is_paid=True).count()

        # Total Completed Orders
        total_completed_orders = Order.objects.filter(status='COMPLETE').count()

        # Total Revenue (Assuming there's a 'total_price' field in the Order model)
        total_revenue = Order.objects.filter(status='COMPLETE').aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0

        # Orders by Status
        orders_by_status = Order.objects.values('status').annotate(count=Count('status'))

        # # Top Food Items (most ordered)
        # top_food_items = Order.objects.values('items__fooditem__name').annotate(count=Count('items__fooditem')).order_by('-count')[:5]

        # Total Redeemed Points
        total_redeemed_points = RedemptionTransaction.objects.aggregate(points_redeemed=Sum('points_redeemed'))['points_redeemed'] or 0

        # Orders in the Last 7 Days (can adjust for other time periods)
        today = now().date()
        last_7_days = today - timedelta(days=7)
        orders_last_7_days = Order.objects.filter(created_at__date__gte=last_7_days, is_paid=True).count()

        # Orders by Day (for the last 7 days)
        orders_by_day = Order.objects.filter(created_at__date__gte=last_7_days, is_paid=True).extra({'day': "DATE(created_at)"}).values('day').annotate(count=Count('id')).order_by('day')

        todays_total_revenue = Order.objects.filter(status='COMPLETE', is_paid=True,updated_at__date__gte=today).aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0


        analytics_data = {
            "total_orders": total_orders,
            "total_completed_orders": total_completed_orders,
            "total_revenue": total_revenue,
            "orders_by_status": orders_by_status,
            "total_redeemed_points": total_redeemed_points,
            "orders_last_7_days": orders_last_7_days,
            "orders_by_day": orders_by_day,
            "todays_total_revenue": todays_total_revenue
        }

        return Response(analytics_data, status=status.HTTP_200_OK)
