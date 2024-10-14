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
from rest_framework.parsers import MultiPartParser, FormParser

from account.permissions import IsAdmin
from .serializers import (CategorySerializer, DiningTableSerializer, FoodItemSerializer, SpecialOfferSerializer)

from customerend.models import Review
from customerend.serializers import ReviewSerializer
from .models import Category, DiningTable, FoodItem, SpecialOffer

# sets up logging for this module
logger = logging.getLogger(__name__)

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
    
    - GET: List all dining tables with filtering, searching, and ordering.
    - POST: Create a new dining table.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

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

    @extend_schema(
        summary="Create a new dining table",
        description="Add a new dining table to the database.",
        request=DiningTableSerializer,
        responses={201: DiningTableSerializer, 400: "Bad Request"}
    )
    def post(self, request, *args, **kwargs):
        """
        Create a new dining table.
        """
        serializer = DiningTableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Logging
            logger.info(f"User {request.user.username} created Dining Table '{serializer.data['table_number']}' successfully.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.error(f"User {request.user.username} failed to create dining table: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiningTableDetailAPIView(APIView):
    """
    API view to retrieve, update, or delete a single dining table.
    
    - GET: Retrieve a specific dining table by UUID.
    - PUT: Full update of the dining table.
    - PATCH: Partial update of the dining table.
    - DELETE: Delete a dining table.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="Retrieve a dining table",
        description="Retrieve the details of a specific dining table by its UUID.",
        responses={200: DiningTableSerializer, 404: "Not Found"}
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve a single dining table by its UUID.
        """
        table_id = kwargs.get('pk')
        table = get_object_or_404(DiningTable, id=table_id)
        serializer = DiningTableSerializer(table)

        # Logging
        logger.info(f"User {request.user.username} retrieved Dining Table '{table.table_number}'.")
        return Response(serializer.data)

    @extend_schema(
        summary="Update dining table (full update)",
        description="Perform a full update of a dining table using its UUID.",
        request=DiningTableSerializer,
        responses={200: DiningTableSerializer, 400: "Bad Request", 404: "Not Found"}
    )
    def put(self, request, *args, **kwargs):
        """
        Full update of a dining table.
        """
        table = get_object_or_404(DiningTable, id=kwargs.get('pk'))
        serializer = DiningTableSerializer(table, data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Logging
            logger.info(f"User {request.user.username} fully updated Dining Table '{table.table_number}'.")
            return Response(serializer.data)
        
        logger.error(f"User {request.user.username} failed to update dining table: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Partially update dining table",
        description="Perform a partial update of a dining table using its UUID.",
        request=DiningTableSerializer,
        responses={200: DiningTableSerializer, 400: "Bad Request", 404: "Not Found"}
    )
    def patch(self, request, *args, **kwargs):
        """
        Partial update of a dining table.
        """
        table = get_object_or_404(DiningTable, id=kwargs.get('pk'))
        serializer = DiningTableSerializer(table, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Logging
            logger.info(f"User {request.user.username} partially updated Dining Table '{table.table_number}'.")
            return Response(serializer.data)

        logger.error(f"User {request.user.username} failed to partially update dining table: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a dining table",
        description="Delete a specific dining table using its UUID.",
        responses={204: None, 404: "Not Found"}
    )
    def delete(self, request, *args, **kwargs):
        """
        Delete a dining table.
        """
        table = get_object_or_404(DiningTable, id=kwargs.get('pk'))
        table.delete()

        # Logging
        logger.info(f"User {request.user.username} deleted Dining Table '{table.table_number}'.")
        return Response({"message": "Dining table deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class FoodItemListView(APIView):
    """
    API view to handle requests for creating and retrieving FoodItems under a specific category.
    Provides filtering, searching, and ordering functionalities.

    Methods:
        - get: Retrieve a list of FoodItems under a given category with optional filters.
        - post: Add a new FoodItem under a specified category.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    #parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Retrieve a list of FoodItems under a specific category",
        parameters=[
            OpenApiParameter(name='search', description='Search food items by name or description', required=False, type=str),
            OpenApiParameter(name='ordering', description='Order by fields like price or created_at', required=False, type=str)
        ],
        responses={200: FoodItemSerializer(many=True)}
    )
    def get(self, request, category_id):
        """
        Retrieve a list of FoodItems under a specific category.
        Handles filtering, searching, and ordering.

        Args:
            category_id (UUID): The UUID of the category.

        Returns:
            Response: A JSON response with the list of food items.
        """
    
        category = get_object_or_404(Category, id=category_id)
        fooditems = FoodItem.objects.filter(category=category)

        # Apply filtering, searching, and ordering
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering', 'created_at')  # Default ordering by created_at

    
        if search:
            fooditems = fooditems.filter(Q(name__icontains=search) | Q(description__icontains=search))

        # Ordering
        fooditems = fooditems.order_by(ordering)

        serializer = FoodItemSerializer(fooditems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(
        summary="Create a new FoodItem under a specific category",
        request=FoodItemSerializer,
        responses={201: FoodItemSerializer, 400: "Bad Request"}
    )
    def post(self, request, category_id):
        """
        Create a new FoodItem under a specific category.

        Args:
            category_id (UUID): The UUID of the category.

        Returns:
            Response: A JSON response with the newly created food item or validation errors.
        """
        serializer = FoodItemSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(category_id=category_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FoodItemDetailView(APIView):
    """
    API view to handle retrieving, updating, and deleting a specific FoodItem.
    logging, and proper validation for each operation.

    Methods:
        - get: Retrieve details of a specific FoodItem.
        - put: Update all fields of a specific FoodItem.
        - patch: Partially update fields of a specific FoodItem.
        - delete: Delete a specific FoodItem.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="Retrieve details of a specific FoodItem",
        responses={200: FoodItemSerializer, 404: "Not Found"}
    )
    def get(self, request, category_id, fooditem_id):
        """
        Retrieve details of a specific FoodItem.

        Args:
            category_id (UUID): The UUID of the category.
            fooditem_id (UUID): The UUID of the food item.

        Returns:
            Response: A JSON response with the food item details or 404 if not found.
        """
        

        
        fooditem = get_object_or_404(FoodItem, id=fooditem_id, category_id=category_id)

        serializer = FoodItemSerializer(fooditem)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update all fields of a specific FoodItem",
        request=FoodItemSerializer,
        responses={200: FoodItemSerializer, 400: "Bad Request", 404: "Not Found"}
    )
    def put(self, request, category_id, fooditem_id):
        """
        Update all fields of a specific FoodItem.

        Args:
            category_id (UUID): The UUID of the category.
            fooditem_id (UUID): The UUID of the food item.

        Returns:
            Response: A JSON response with the updated food item details or validation errors.
        """
        fooditem = get_object_or_404(FoodItem, id=fooditem_id, category_id=category_id)
        serializer = FoodItemSerializer(fooditem, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Food item '{fooditem.name}' updated successfully.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        logger.error(f"Failed to update food item: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
        summary="Partially update fields of a specific FoodItem",
        request=FoodItemSerializer,
        responses={200: FoodItemSerializer, 400: "Bad Request", 404: "Not Found"}
    )
    def patch(self, request, category_id, fooditem_id):
        """
        Partially update fields of a specific FoodItem.

        Args:
            category_id (UUID): The UUID of the category.
            fooditem_id (UUID): The UUID of the food item.

        Returns:
            Response: A JSON response with the updated food item details or validation errors.
        """
        fooditem = get_object_or_404(FoodItem, id=fooditem_id, category_id=category_id)
        serializer = FoodItemSerializer(fooditem, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Food item '{fooditem.name}' partially updated successfully.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        logger.error(f"Failed to partially update food item: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
        summary="Delete a specific FoodItem",
        responses={204: None, 404: "Not Found"}
    )
    def delete(self, request, category_id, fooditem_id):
        """
        Delete a specific FoodItem.

        Args:
            category_id (UUID): The UUID of the category.
            fooditem_id (UUID): The UUID of the food item.

        Returns:
            Response: A status 204 response on successful deletion or 404 if not found.
        """
        fooditem = get_object_or_404(FoodItem, id=fooditem_id, category_id=category_id)
        fooditem.delete()
        
        logger.info(f"Food item '{fooditem.name}' deleted successfully.")
        return Response(status=status.HTTP_204_NO_CONTENT)
