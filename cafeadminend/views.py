import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.exceptions import ValidationError

from account.permissions import IsAdmin
from .models import Category, DiningTable, FoodItem, SpecialOffer
from .serializers import CategorySerializer, DiningTableSerializer, FoodItemSerializer, SpecialOfferSerializer


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
    API view to retrieve list of categories or create a new category.

    - GET: Returns a list of all categories with filtering, searching, and ordering.
    - POST: Creates a new category if valid data is provided.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        """
        Retrieves a list of categories with optional filtering, searching, and ordering.

        - Filters: ?name=fruits
        - Search: ?search=fruit
        - Order: ?ordering=-created_at
        """
        logger.debug("Fetching all categories with filters and search options")

        # Apply filtering, searching, and ordering
        categories = Category.objects.all()

        if categories.exists():
            name_filter = request.query_params.get('name')
            search_query = request.query_params.get('search')
            ordering = request.query_params.get('ordering', 'created_at')

            # Filtering by name
            if name_filter:
                categories = categories.filter(name__icontains=name_filter)

            # Searching in name and description
            if search_query:
                categories = categories.filter(
                    name__icontains=search_query
                ) | categories.filter(
                    description__icontains=search_query
                )

            # Ordering
            if ordering:
                categories = categories.order_by(ordering)

            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        logger.info("No categories found.")
        return Response({"detail":"No Categories available."}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Create a new category.

        If the category name already exists, raise a ValidationError.
        """
        logger.debug("Attempting to create a new category")
        name = request.data.get('name')
        if Category.objects.filter(name=name).exists():
            logger.error(f"Category '{name}' already exists")
            raise ValidationError(f"Category '{name}' already exists.")

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Category '{name}' created successfully.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Failed to create category. Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Cache the list of categories for 1 minutes
    @method_decorator(cache_page(60 * 1))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class CategoryDetailAPIView(APIView):
    """
    API view to retrieve, update, or delete a category.

    - GET: Retrieves details of a category by ID.
    - PUT/PATCH: Updates an existing category.
    - DELETE: Deletes a category.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve a single category by ID.
        """
        category = self.get_object(pk)
        if not category:
            logger.error(f"Category with ID {pk} not found.")
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category)
        logger.debug(f"Fetched details for category with ID {pk}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        """
        Update a category by ID.
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
        
    def patch(self, request, pk, *args, **kwargs):
        """
        Partial update of a category.
        """
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Category '{category.name}' partially updated successfully.")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """
        Delete a category by ID.
        """
        category = self.get_object(pk)
        if not category:
            logger.error(f"Category with ID {pk} not found.")
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        category.delete()
        logger.warning(f"Category with ID {pk} deleted.")
        return Response({"message": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    # Cache the category detail for 1 minutes
    @method_decorator(cache_page(60 * 1))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)



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
        Retrieve the SpecialOffer for a given food item, if it is active.
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
