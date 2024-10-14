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
from .serializers import (CategorySerializer, DiningTableSerializer, FoodItemSerializer, SpecialOfferSerializer, NotificationSerializer, RedemptionOptionSerializer, RedemptionTransactionSerializer)

from customerend.models import Review
from customerend.serializers import ReviewSerializer
from menu.models import Category, DiningTable, FoodItem, SpecialOffer


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
                 

class CategoryListCreateAPIView(APIView):
    """
    API view to retrieve the list of categories or create a new category.

    **GET**: Retrieves all categories with optional filtering, searching, and ordering.

    **POST**: Creates a new category if valid data is provided.

    **Permissions**:
        - Only authenticated users with admin role can create a category.

    **Query Parameters**:
        - `name` (str): Optional filter by category name.
        - `search` (str): Optional search query for name or description.
        - `ordering` (str): Optional field for ordering categories.

    **Responses**:
        - **200 OK**: List of categories.
        - **201 Created**: Created category details.
        - **400 Bad Request**: Invalid input data.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

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
    
    @extend_schema(
        request=CategorySerializer,
        responses={
            201: CategorySerializer,
            400: OpenApiExample("Validation error.", response_only=True, value={"name": "Category with this name already exists."}),
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Create a new category.

        Body Parameters:
            name (str): Name of the category.
            description (str): Description of the category.

        Returns:
            Response (JSON): Created category details or errors.
        """

        logger.debug("Attempting to create a new category")

        name = request.data.get('name')
        if Category.objects.filter(name=name).exists():
            logger.error(f"Category '{name}' already exists")
            return Response({"error": f"Category '{name}' already exists."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Category '{name}' created successfully.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Failed to create category. Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailAPIView(APIView):
    """
    API view to retrieve, update, or delete a specific category.

    **GET**: Retrieves a single category by ID.

    **PUT/PATCH**: Updates an existing category.

    **DELETE**: Deletes a category by ID.

    **Permissions**:
        - Only authenticated users with admin role can update or delete a category.

    **Path Parameters**:
        - `pk` (UUID): The ID of the category to retrieve, update, or delete.

    **Responses**:
        - **200 OK**: Category details.
        - **204 No Content**: Category successfully deleted.
        - **400 Bad Request**: Invalid input data.
        - **404 Not Found**: Category not found.
    """
     
    permission_classes = [IsAuthenticated, IsAdmin]

    
    def get_object(self, pk):
        """
        Retrieve a category instance by its primary key.
        """
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None
        
    @extend_schema(
        responses={
            200: CategorySerializer,
            404: OpenApiExample("Category not found.", response_only=True, value={"detail": "Category not found."}),
        }
    )
    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve category details by ID.

        Path Parameters:
            pk (UUID): The ID of the category.

        Returns:
            Response (JSON): Category details or error message if not found.
        """

        category = self.get_object(pk)
        if not category:
            logger.error(f"Category with ID {pk} not found.")
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category)
        logger.debug(f"Fetched details for category with ID {pk}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: OpenApiExample("Validation error.", response_only=True, value={"detail": "Invalid data."}),
        }
    )
    def put(self, request, pk, *args, **kwargs):
        """
        Update a category by ID.

        Path Parameters:
            pk (UUID): The ID of the category.

        Body Parameters:
            name (str): The new name of the category.
            description (str): The new description of the category.

        Returns:
            Response (JSON): Updated category details or error message if invalid.
        """

        category = self.get_object(pk)
        if not category:
            logger.error(f"Category with ID {pk} not found.")
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Category with ID {pk} updated successfully.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            logger.error(f"Failed to update category with ID {pk}. Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: OpenApiExample("Validation error.", response_only=True, value={"detail": "Invalid data."}),
        }
    ) 
    def patch(self, request, pk, *args, **kwargs):
        """
        Partially update a category by ID.

        Path Parameters:
            pk (UUID): The ID of the category.

        Body Parameters:
            name (str): The new name of the category (optional).
            description (str): The new description of the category (optional).

        Returns:
            Response (JSON): Updated category details or error message if invalid.
        """

        category = self.get_object(pk)
        if not category:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Category '{category.name}' partially updated successfully.")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            204: OpenApiExample("Category deleted successfully.", response_only=True, value={"message": "Category deleted successfully."}),
            404: OpenApiExample("Category not found.", response_only=True, value={"detail": "Category not found."}),
        }
    )
    def delete(self, request, pk, *args, **kwargs):
        """
        Delete a category by ID.

        Path Parameters:
            pk (UUID): The ID of the category.

        Returns:
            Response (JSON): Success message or error if not found.
        """

        category = self.get_object(pk)
        if not category:
            logger.error(f"Category with ID {pk} not found.")
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        category.delete()
        logger.warning(f"Category with ID {pk} deleted.")
        return Response({"message": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



class DiningTableListAPIView(APIView):
    """
    API view to retrieve and create dining tables.
    
    - GET: List all dining tables (with filtering, searching, and ordering).
    - POST: Create a new dining table.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        """
        List all dining tables with, filtering, searching, and ordering.
        Cached for 5 minutes.
        """
        cache_key = "dining_table_list"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.debug("Serving dining table list from cache.")
            return Response(cached_data)

        tables = DiningTable.objects.all()

        # Filter by table_number
        table_number = request.query_params.get('table_number', None)
        if table_number:
            tables = tables.filter(table_number=table_number)

        # Search
        search = request.query_params.get('search', None)
        if search:
            tables = tables.filter(table_number__icontains=search)

        # Ordering
        ordering = request.query_params.get('ordering', 'created_at')
        if ordering.startswith('-'):
            tables = tables.order_by(ordering)
        else:
            tables = tables.order_by(ordering)

        
        serializer = DiningTableSerializer(tables, many=True)

        cache.set(cache_key, serializer.data, timeout=300)  # Cache for 5 minutes
        logger.debug("Caching dining table list for 5 minutes.")

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        """
        Create a new dining table.
        """
        serializer = DiningTableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Clear the cache for the dinning table when a new one is added
            cache.delete('dining_table_list')

            logger.info(f"Dining Table '{serializer.data['table_number']}' created successfully.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Failed to create dining table: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiningTableDetailAPIView(APIView):
    """
    API view to retrieve, update, or delete a single dining table.
    
    - GET: Retrieve a specific dining table.
    - PUT: Update the entire dining table (full update).
    - PATCH: Update part of the dining table (partial update).
    - DELETE: Delete a dining table.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        """
        Retrieve a single dining table by its UUID.
        Cached for 5 minutes.
        """
        table_id = kwargs.get('pk')
        cache_key = f"dining_table_{table_id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.debug(f"Serving dining table {table_id} from cache.")
            return Response(cached_data)

        table = get_object_or_404(DiningTable, id=table_id)
        serializer = DiningTableSerializer(table)

        cache.set(cache_key, serializer.data, timeout=300)  # Cache for 5 minutes
        logger.debug(f"Caching dining table {table_id} for 5 minutes.")

        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        """
        Full update of a dining table.
        """
        table = get_object_or_404(DiningTable, id=kwargs.get('pk'))
        serializer = DiningTableSerializer(table, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Dining Table '{table.table_number}' updated successfully.")
            return Response(serializer.data)
        logger.error(f"Failed to update dining table: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        """
        Partial update of a dining table.
        """
        table = get_object_or_404(DiningTable, id=kwargs.get('pk'))
        serializer = DiningTableSerializer(table, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Dining Table '{table.table_number}' partially updated successfully.")
            return Response(serializer.data)
        logger.error(f"Failed to partially update dining table: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        Delete a dining table.
        """
        table = get_object_or_404(DiningTable, id=kwargs.get('pk'))
        table.delete()
        logger.info(f"Dining Table '{table.table_number}' deleted successfully.")
        return Response({"message": "Dining table deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class FoodItemListView(APIView):
    """
    API view to handle requests for creating and retrieving FoodItems under a specific category.
    Provides filtering, searching, and ordering functionalities with caching to reduce database load.

    Methods:
        - get: Retrieve a list of FoodItems under a given category with optional filters.
        - post: Add a new FoodItem under a specified category.
    """
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['category', 'is_available']
    ordering_fields = ['price', 'created_at']
    search_fields = ['name', 'description']
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, category_id):
        """
        Retrieve a list of FoodItems under a specific category.

        Uses caching to store the result for 15 minutes.
        Provides filtering, searching, and ordering capabilities.

        Args:
            category_id (UUID): The UUID of the category.

        Returns:
            Response: A JSON response with the list of food items.
        """
        cache_key = f'fooditems_category_{category_id}'
        fooditems = cache.get(cache_key)

        if not fooditems:
            # If cache is empty, query the database and store the result in cache
            fooditems = FoodItem.objects.filter(category_id=category_id)
            cache.set(cache_key, fooditems, timeout=60 * 1)  # Cache for 1 minute

        #fooditems = self.filter_queryset(fooditems)
        serializer = FoodItemSerializer(fooditems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, category_id):
        """
        Create a new FoodItem under a specific category.

        On success, the cache for this category is cleared.

        Args:
            category_id (UUID): The UUID of the category.

        Returns:
            Response: A JSON response with the newly created food item or validation errors.
        """
        serializer = FoodItemSerializer(data=request.data)
        #category = get_object_or_404(Category, id=category_id)
        if serializer.is_valid():
            serializer.save(category_id=category_id)
            # Clear the cache for the category when a new food item is added
            cache.delete(f'fooditems_category_{category_id}')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FoodItemDetailView(APIView):
    """
    API view to handle retrieving, updating, and deleting a specific FoodItem.

    Methods:
        - get: Retrieve details of a specific FoodItem.
        - put: Update all fields of a specific FoodItem.
        - patch: Partially update fields of a specific FoodItem.
        - delete: Delete a specific FoodItem.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, category_id, fooditem_id):
        """
        Retrieve details of a specific FoodItem.

        Args:
            category_id (UUID): The UUID of the category.
            fooditem_id (UUID): The UUID of the food item.

        Returns:
            Response: A JSON response with the food item details or 404 if not found.
        """
        fooditem = FoodItem.objects.filter(id=fooditem_id, category_id=category_id).first()
        if fooditem:
            serializer = FoodItemSerializer(fooditem)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, category_id, fooditem_id):
        """
        Update all fields of a specific FoodItem.

        Args:
            category_id (UUID): The UUID of the category.
            fooditem_id (UUID): The UUID of the food item.

        Returns:
            Response: A JSON response with the updated food item details or validation errors.
        """
        fooditem = FoodItem.objects.filter(id=fooditem_id, category_id=category_id).first()
        if fooditem:
            serializer = FoodItemSerializer(fooditem, data=request.data)
            if serializer.is_valid():
                serializer.save()
                cache.delete(f'fooditems_category_{category_id}')
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, category_id, fooditem_id):
        """
        Partially update fields of a specific FoodItem.

        Args:
            category_id (UUID): The UUID of the category.
            fooditem_id (UUID): The UUID of the food item.

        Returns:
            Response: A JSON response with the updated food item details or validation errors.
        """
        fooditem = FoodItem.objects.filter(id=fooditem_id, category_id=category_id).first()
        if fooditem:
            serializer = FoodItemSerializer(fooditem, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                cache.delete(f'fooditems_category_{category_id}')
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, category_id, fooditem_id):
        """
        Delete a specific FoodItem.

        Args:
            category_id (UUID): The UUID of the category.
            fooditem_id (UUID): The UUID of the food item.

        Returns:
            Response: A status 204 response on successful deletion or 404 if not found.
        """
        fooditem = FoodItem.objects.filter(id=fooditem_id, category_id=category_id).first()
        if fooditem:
            fooditem.delete()
            cache.delete(f'fooditems_category_{category_id}')
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class SpecialOfferListAPIView(APIView):
    """
    API view to list all SpecialOffers.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, format=None):
        """
        Retrieve the SpecialOffer if it is active.
        """
    
        special_offers = SpecialOffer.objects.all()
        serializer = SpecialOfferSerializer(special_offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SpecialOfferCreateAPIView(APIView):
    """
    API view to handle creating a new SpecialOffer.
    """
       
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, fooditem_id, format=None):
        """
        Create a new SpecialOffer for a given food item.
        """
        try:
            fooditem = FoodItem.objects.get(id=fooditem_id)
        except FoodItem.DoesNotExist:
            logger.warning("Active FoodItem with id %s not found.", fooditem_id)
            return Response({"detail": "Active FoodItem not found."}, status=status.HTTP_404_NOT_FOUND)

        offer = get_object_or_404(SpecialOffer, fooditem=fooditem)

        if offer:
            return Response({"message":"Specialoffer with this fooditem already exists"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SpecialOfferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(fooditem=fooditem)
            logger.info("SpecialOffer created successfully for FoodItem id %s.", fooditem_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error("Failed to create SpecialOffer: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpecialOfferDetailAPIView(APIView):
    """
    API view to handle operations on a single SpecialOffer.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, offer_id):
        """
        Retrieve the SpecialOffer object by its associated id.
        """
        try:
            return SpecialOffer.objects.get(id=offer_id)
        except (SpecialOffer.DoesNotExist):
            logger.warning("No active SpecialOffer found for this id %s.", offer_id)
            return None

    def get(self, request, offer_id, format=None):
        """
        Retrieve a SpecialOffer by its associated food item.
        """
        special_offer = self.get_object(offer_id)
        if special_offer:
            serializer = SpecialOfferSerializer(special_offer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "SpecialOffer not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, offer_id, format=None):
        """
        Update a SpecialOffer by its associated food item.
        """
        special_offer = self.get_object(offer_id)
        if special_offer:
            serializer = SpecialOfferSerializer(special_offer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info("SpecialOffer updated successfully for FoodItem id %s.", offer_id)
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.error("Failed to update SpecialOffer: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "SpecialOffer not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, offer_id, format=None):
        """
        Delete a SpecialOffer by its associated food item.
        """
        special_offer = self.get_object(offer_id)
        if special_offer:
            special_offer.delete()
            logger.info("SpecialOffer deleted successfully for FoodItem id %s.", offer_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "SpecialOffer not found."}, status=status.HTTP_404_NOT_FOUND)


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
       
