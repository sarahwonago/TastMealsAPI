import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view, OpenApiExample

from account.permissions import IsAdmin
from .models import Notification, RedemptionOption, RedemptionTransaction
from .serializers import (NotificationSerializer, RedemptionOptionSerializer, RedemptionTransactionSerializer)

from review.models import Review
from review.serializers import ReviewSerializer
from menu.models import FoodItem

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
    View to list all notifications for the authenticated user with filtering, searching, and ordering.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

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
        
        # Ordering by created_at
        ordering = request.query_params.get('ordering', '-updated_at')  # Default ordering by most recent
        notifications = notifications.order_by(ordering)

    
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NotificationDetailView(APIView):
    """
    View to retrieve a single notification and mark it as read.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)

        # Mark as read when viewed
        if not notification.is_read:
            notification.is_read = True
            notification.save()

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Deletes a single notification.
        """
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.delete()
        return Response({"detail": "Notification deleted."}, status=status.HTTP_204_NO_CONTENT)


class BulkMarkAsReadView(APIView):
    """
    View to mark multiple notifications as read for the authenticated user.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request):
        notification_ids = request.data.get('notification_ids', [])
        user = request.user

        if not notification_ids:
            return Response({"detail": "No notification IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        notifications = Notification.objects.filter(id__in=notification_ids, user=user)
        if not notifications.exists():
            return Response({"detail": "No matching notifications found."}, status=status.HTTP_404_NOT_FOUND)

        notifications.update(is_read=True)
        return Response({"detail": "Notifications marked as read."}, status=status.HTTP_200_OK)

class BulkDeleteNotificationsView(APIView):
    """
    View to delete multiple notifications for the authenticated user.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request):
        notification_ids = request.data.get('notification_ids', [])
        user = request.user

        if not notification_ids:
            return Response({"detail": "No notification IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        notifications = Notification.objects.filter(id__in=notification_ids, user=user)
        if not notifications.exists():
            return Response({"detail": "No matching notifications found."}, status=status.HTTP_404_NOT_FOUND)

        notifications.delete()
        return Response({"detail": "Notifications deleted."}, status=status.HTTP_204_NO_CONTENT)
    

class RedemptionOptionListCreateView(APIView):
    """
    Handles the creation and listing of RedemptionOptions using APIView.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        """
        Fetches all redemption options.
        """
        options = RedemptionOption.objects.all()
        
        # Filtering, Searching, Ordering
        points_required = request.query_params.get('points_required', None)
        search_query = request.query_params.get('search', None)
        ordering = request.query_params.get('ordering', None)

        if points_required:
            options = options.filter(points_required=points_required)
        if search_query:
            options = options.filter(fooditem__name__icontains=search_query) | options.filter(description__icontains=search_query)
        if ordering:
            options = options.order_by(ordering)

        serializer = RedemptionOptionSerializer(options, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = RedemptionOptionSerializer(data=request.data)

        fooditem_id = request.data.get('fooditem_id')

        fooditem = get_object_or_404(FoodItem, id=fooditem_id)

        # checks if the redemption option with passed fooditem exists
        # fix this 
        # try:
            
        #     redemption_option = get_object_or_404(RedemptionOption, fooditem=fooditem)
        #     return Response({"detail":"A redemption option with that fooditem already exists."}, status=status.HTTP_400_BAD_REQUEST)
        # except RedemptionOption.DoesNotExist:
        #     pass

        redemption_option = RedemptionOption.objects.filter(fooditem=fooditem)

        # checks if the redemption option with passed fooditem exists
        if redemption_option:
            return Response({"detail":"A redemption option with that fooditem already exists."}, status=status.HTTP_400_BAD_REQUEST)
            
        if serializer.is_valid():
            serializer.save(fooditem=fooditem)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RedemptionOptionDetailView(APIView):
    """
    Handles the retrieval, update, and deletion of a single RedemptionOption using APIView.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        try:
            return RedemptionOption.objects.get(pk=pk)
        except RedemptionOption.DoesNotExist:
            raise ValidationError("Redemption Option not found")

    def get(self, request, pk, *args, **kwargs):
        option = self.get_object(pk)
        serializer = RedemptionOptionSerializer(option)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        option = self.get_object(pk)
        serializer = RedemptionOptionSerializer(option, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        option = self.get_object(pk)
        option.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
            


class RedemptionTransactionListView(APIView):
    """
    Handles the listing of RedemptionTransactions using APIView.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        transactions = RedemptionTransaction.objects.all()
        
        # Filtering, Searching, Ordering
        status_filter = request.query_params.get('status', None)
        search_query = request.query_params.get('search', None)
        ordering = request.query_params.get('ordering', None)

        if status_filter:
            transactions = transactions.filter(status=status_filter)
        if search_query:
            transactions = transactions.filter(redemption_option__fooditem__name__icontains=search_query)
        if ordering:
            transactions = transactions.order_by(ordering)

        serializer = RedemptionTransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class RedemptionTransactionDetailView(APIView):
    """
    Handles retrieval, update, and deletion of RedemptionTransaction.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        try:
            return RedemptionTransaction.objects.get(pk=pk)
        except RedemptionTransaction.DoesNotExist:
            raise ValidationError("Transaction not found")

    def get(self, request, pk, *args, **kwargs):
        transaction = self.get_object(pk)
        serializer = RedemptionTransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def delete(self, request, pk, *args, **kwargs):
        transaction = self.get_object(pk)
        
        if transaction.status == 'DELIVERED':
            transaction.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message":"You cannot delete if not delivered"}, status=status.HTTP_400_BAD_REQUEST)
        
    

class MarkRedemptionTransactionDeliveredView(APIView):
    """
    Handles marking a RedemptionTransaction as delivered.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        try:
            return RedemptionTransaction.objects.get(pk=pk)
        except RedemptionTransaction.DoesNotExist:
            raise ValidationError("Transaction not found")

    def patch(self, request, pk, *args, **kwargs):

        #fix this, send the status in the body
        transaction = self.get_object(pk)
        transaction.status = 'DELIVERED'
        transaction.save()
        serializer = RedemptionTransactionSerializer(transaction)
    
        return Response(serializer.data, status=status.HTTP_200_OK)
       
