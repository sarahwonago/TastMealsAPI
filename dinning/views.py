import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view, OpenApiExample

from account.permissions import IsAdmin
from .serializers import DiningTableSerializer


from .models import DiningTable

# sets up logging for this module
logger = logging.getLogger(__name__)
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
