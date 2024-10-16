import logging
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from drf_spectacular.utils import OpenApiParameter, extend_schema, OpenApiExample, OpenApiResponse, inline_serializer

from rest_framework import serializers
from cafeadminend.models import  RedemptionOption, RedemptionTransaction
from menu.models import Category, FoodItem, SpecialOffer, DiningTable
from cafeadminend.serializers import RedemptionOptionSerializer

from notification.models import Notification
from notification.serializers import NotificationSerializer

from menu.serializers import (CategorySerializer, DiningTableSerializer, FoodItemSerializer, SpecialOfferSerializer)
from .serializers import CustomerLoyaltyPointSerializer
from .models import CustomerLoyaltyPoint

from account.permissions import IsCustomer

logger = logging.getLogger(__name__)

class CustomerHomeAPIView(APIView):
    """
    Handles the customer dashboard endpoint.
    Customer must be authenticated.
    """

    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        logger.info(f"Customer {request.user.username} accessed customer home.")

        return Response({"message":"Welcome home customer"}, status=status.HTTP_200_OK)
    

class CategoryListAPIView(APIView):
    """
    API view to retrieve list of all categories.

    - GET: Returns a list of all categories with filtering, searching, and ordering.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="name", description="Filter by category name", required=False, type=str),
            OpenApiParameter(name="search", description="Search within category name and description", required=False, type=str),
            OpenApiParameter(name="ordering", description="Order by a specific field (e.g., '-created_at')", required=False, type=str),
        ],
        responses={
            200: CategorySerializer(many=True),
            404: OpenApiExample("No categories found.", response_only=True, value={"detail": "No categories found."})
        }
    )
    def get(self, request, *args, **kwargs):
        """
        **GET**:Retrieves a list of categories with optional filtering, searching, and ordering.

        URL Parameters:
            name (str): Filter by category name.?name=fruits
            search (str): Search categories by name or description.?search=fruit
            ordering (str): Order by specified field, default is created_at.?ordering=-created_at

        Returns:
            Response (JSON): List of categories.
        """
       
        logger.debug("Fetching all categories with filters and search options")

        categories = Category.objects.all()

        # checks if name, search, ordering query params have been passed
        name_filter = request.query_params.get('name')
        search_query = request.query_params.get('search')
        ordering = request.query_params.get('ordering', 'created_at')

        # applying filters, search and ordering
        if name_filter:
            categories = categories.filter(name__icontains=name_filter)

        if search_query:
            categories = categories.filter(
                name__icontains=search_query
            ) | categories.filter(
                description__icontains=search_query
            )

        if ordering:
            categories = categories.order_by(ordering)

        if categories.exists():
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        logger.info("No categories found.")
        return Response({"detail": "No Categories available."}, status=status.HTTP_200_OK)
    
class CategoryDetailAPIView(APIView):
    """
    API view to retrieve  fooditems under specific category.

    - GET: Retrieves all fooditems under a specific category.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve fooditems under specific category.
        """
        category = self.get_object(pk)

        if not category:
            logger.error(f"Category with ID {pk} not found.")
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        
        fooditems = FoodItem.objects.filter(category=category)
        #serializer = CategorySerializer(category)
        serializer = FoodItemSerializer(fooditems, many=True)
        logger.debug(f"Fetched details for category with ID {pk}")

        # modify to include fooditems under this category
        return Response(serializer.data, status=status.HTTP_200_OK)

class FoodItemListAPIView(APIView):
    """
    API view to retrieve all fooditems.

    - GET: Returns a list of all fooditems with filtering, searching, and ordering.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="name", description="Filter by fooditem name", required=False, type=str),
            OpenApiParameter(name="search", description="Search within fooditem name and description", required=False, type=str),
            OpenApiParameter(name="ordering", description="Order by a specific field (e.g., '-created_at')", required=False, type=str),
        ],
        responses={
            200: FoodItemSerializer(many=True),
            404: OpenApiExample("No fooditems found.", response_only=True, value={"detail": "No fooditems found."})
        }
    )
    def get(self, request, *args, **kwargs):
        """
        **GET**:Retrieves a list of all fooditems with optional filtering, searching, and ordering.

        URL Parameters:
            name (str): Filter by fooditem name.?name=rice
            search (str): Search fooditems by name or description.?search=rice
            ordering (str): Order by specified field, default is created_at.?ordering=-created_at

        Returns:
            Response (JSON): List of fooditems.
        """
       
        logger.debug("Fetching all fooditems with filters and search options")

        fooditems = FoodItem.objects.filter(is_available=True)

        # checks if name, search, ordering query params have been passed
        name_filter = request.query_params.get('name')
        search_query = request.query_params.get('search')
        ordering = request.query_params.get('ordering', 'created_at')

        # applying filters, search and ordering
        if name_filter:
            fooditems = fooditems.filter(name__icontains=name_filter)

        if search_query:
            fooditems = fooditems.filter(
                name__icontains=search_query
            ) | fooditems.filter(
                description__icontains=search_query
            )

        if ordering:
            fooditems = fooditems.order_by(ordering)

        if fooditems.exists():
            serializer = FoodItemSerializer(fooditems, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        logger.info("No fooditems found.")
        return Response({"detail": "No fooditems available."}, status=status.HTTP_200_OK)
    
class DiningTableListAPIView(APIView):
    """
    API view to retrieve dining tables.
    
    - GET: List all dining tables (with filtering, searching, and ordering).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all dining tables",
        description="Retrieve a list of all dining tables. Supports filtering, searching, and ordering.",
        parameters=[
            OpenApiParameter("table_number", str, description="Filter by table number"),
            OpenApiParameter("search", str, description="Search by table number (partial match)"),
            OpenApiParameter("ordering", str, description="Order by field, default is 'created_at'. Use '-' for descending order.")
        ],
        responses={200: DiningTableSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        """
        List all dining tables with filtering, searching, and ordering.
        """
        tables = DiningTable.objects.all()

        # Filtering
        table_number = request.query_params.get('table_number', None)
        if table_number:
            tables = tables.filter(table_number=table_number)

        # Searching
        search = request.query_params.get('search', None)
        if search:
            tables = tables.filter(table_number__icontains=search)

        # Ordering
        ordering = request.query_params.get('ordering', 'created_at')
        tables = tables.order_by(ordering)

        serializer = DiningTableSerializer(tables, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class SpecialOfferListAPIView(APIView):
    """
    API view to list all SpecialOffers.
    """

    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request, format=None):
        """
        Retrieve all the SpecialOffer  if it is active.
        """
    
        special_offers = SpecialOffer.objects.all()
        serializer = SpecialOfferSerializer(special_offers, many=True)
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
    permission_classes = [IsAuthenticated, IsCustomer]

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
    permission_classes = [IsAuthenticated, IsCustomer]

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
    permission_classes = [IsAuthenticated, IsCustomer]

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

class CustomerLoyaltyPointView(APIView):
    """
    Endpoint to view customer loyalty points.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        try:
            customer_points = CustomerLoyaltyPoint.objects.get(user=request.user)
            serializer = CustomerLoyaltyPointSerializer(customer_points)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomerLoyaltyPoint.DoesNotExist:
            return Response({"detail": "Loyalty points not found."}, status=status.HTTP_404_NOT_FOUND)
        
class RedemptionOptionListView(APIView):
    """
    Handles the creation and listing of RedemptionOptions using APIView.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

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

class RedeemLoyaltyPointsAPIView(APIView):
    """
    Endpoint to redeem customer loyalty points.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request,redemption_id, *args, **kwargs):
        redemption_option = RedemptionOption.objects.get(id=redemption_id)
        points_required = redemption_option.points_required
        user = request.user

        # Check if user has enough points
        if user.customerloyaltypoint.points < points_required:
            return Response({"message":"You don't have enough points to redeem this option."},status=status.HTTP_400_BAD_REQUEST)

        # Deduct points
        user.customerloyaltypoint.points -= points_required
        user.customerloyaltypoint.save()

        # Create Redemption Transaction
        transaction = RedemptionTransaction.objects.create(
            customer=user,
            redemption_option=redemption_option,
            points_redeemed=points_required,
        )

        # send notification to user
        Notification.objects.create(
            user=user,
            message=f"You have redeemed {points_required} for {redemption_option.fooditem}. Go pick it up at the counter",

        )
        
        
        return Response({"message":f"Successfully redeemed {points_required}. points"}, status=status.HTTP_201_CREATED)