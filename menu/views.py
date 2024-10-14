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


