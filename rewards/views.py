import logging
import uuid
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample, inline_serializer

from account.permissions import IsAdmin
from .models import RedemptionOption, RedemptionTransaction
from .serializers import RedemptionOptionSerializer, RedemptionTransactionSerializer


from menu.models import FoodItem

# sets up logging for this module
logger = logging.getLogger(__name__)

class RedemptionOptionListCreateView(APIView):
    """
    Handles the creation and listing of RedemptionOptions using APIView.

    Query Parameters:
    - points_required (int, optional): Filter redemption options by points required.
    - search (str, optional): Search redemption options by food item name or description.
    - ordering (str, optional): Order by any field (default is by creation date).
    
    Responses:
    - 200: Success, list of redemption options.
    - 201: Created, new redemption option.
    - 400: Invalid request data or duplicate redemption option.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='points_required', description='Filter by points required', required=False, type=int),
            OpenApiParameter(name='search', description='Search by food item or description', required=False, type=str),
        ],
        responses={
            200: RedemptionOptionSerializer(many=True),
            400: OpenApiResponse(description="Invalid request or query."),
        },
        summary="List all redemption options"
    )
    def get(self, request, *args, **kwargs):
        """
        Fetch all redemption options with filtering, searching, and ordering.
        """
        options = RedemptionOption.objects.all()

        # Filtering by points required
        points_required = request.query_params.get('points_required')
        if points_required:
            options = options.filter(points_required=points_required)

        # Searching by food item name or description
        search_query = request.query_params.get('search')
        if search_query:
            options = options.filter(Q(fooditem__name__icontains=search_query) | Q(description__icontains=search_query))


        serializer = RedemptionOptionSerializer(options, many=True)
        logger.info(f"Redemption options listed for admin {request.user.username}.")
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @extend_schema(
        request=RedemptionOptionSerializer,
        responses={
            201: RedemptionOptionSerializer,
            400: OpenApiResponse(description="A redemption option with this food item already exists."),
        },
        summary="creates a new redemption option",
        description="""
        Create a new redemption option by passing the `fooditem_id` in the request body.

        **Request Example**:
        ```
        {
            "fooditem_id": 123,  # ID of the food item to create a redemption option for
            "points_required": 100,  # Points required to redeem this option
            "description": "Redeem for a delicious burger"  # Optional description
        }
        ```
        """
    )
    def post(self, request, *args, **kwargs):
        """
        Create a new redemption option by passing the fooditem_id in the request body.

        - **fooditem_id**: The ID of the food item for which the redemption option is being created.
        - **points_required**: Number of points required to redeem this option.
        - **description**: Optional description of the redemption option.

        **Note**: Ensure that the food item exists and that a redemption option does not already exist for this item.
        """
        serializer = RedemptionOptionSerializer(data=request.data)

        fooditem_id = request.data.get('fooditem_id')

        if not fooditem_id:
            logger.error(f"Food item ID not provided by {request.user.username}.")
            return Response({"detail": "Food item ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the food item exists
        fooditem = get_object_or_404(FoodItem, id=fooditem_id)

        # Check if a redemption option with the same food item already exists
        if RedemptionOption.objects.filter(fooditem=fooditem).exists():
            logger.warning(f"Attempted to create a duplicate redemption option for food item {fooditem.id}.")
            return Response({"detail": "A redemption option with that food item already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save
        if serializer.is_valid():
            serializer.save(fooditem=fooditem)
            logger.info(f"Redemption option created for food item {fooditem.id} by admin {request.user.username}.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f"Invalid data provided by admin {request.user.username}.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class RedemptionOptionDetailView(APIView):
    """
    Handles retrieval, updating, and deletion of a single RedemptionOption.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        try:
            return RedemptionOption.objects.get(pk=pk)
        except RedemptionOption.DoesNotExist:
            logger.error(f"Redemption option {pk} not found.")
            raise ValidationError("Redemption Option not found")

    @extend_schema(
        responses={
            200: RedemptionOptionSerializer,
            404: OpenApiResponse(description="Redemption Option not found."),
        },
        summary="detail redemption option"
    )
    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve a single redemption option.
        """
        option = self.get_object(pk)
        serializer = RedemptionOptionSerializer(option)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=RedemptionOptionSerializer,
        responses={
            200: RedemptionOptionSerializer,
            400: OpenApiResponse(description="Invalid data."),
        },
        summary="uppdates a redemption option"
    )
    def put(self, request, pk, *args, **kwargs):
        """
        Update a redemption option.
        """
        option = self.get_object(pk)
        serializer = RedemptionOptionSerializer(option, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Redemption option {pk} updated by admin {request.user.username}.")
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.error(f"Invalid update data for redemption option {pk}.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Redemption option deleted."),
            404: OpenApiResponse(description="Redemption Option not found."),
        },
        summary="deletes a redemption option"
    )
    def delete(self, request, pk, *args, **kwargs):
        """
        Delete a redemption option.
        """
        option = self.get_object(pk)
        option.delete()
        logger.info(f"Redemption option {pk} deleted by admin {request.user.username}.")
        return Response(status=status.HTTP_204_NO_CONTENT)


class RedemptionTransactionListView(APIView):
    """
    Handles the listing of RedemptionTransactions using APIView.
    
    Query Parameters:
    - status (str, optional): Filter by transaction status.
    - search (str, optional): Search by food item name.
    - ordering (str, optional): Order by field.

    Responses:
    - 200: Success, list of transactions.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='status', description='Filter by transaction status', required=False, type=str),
            OpenApiParameter(name='search', description='Search by food item name', required=False, type=str),
            OpenApiParameter(name='ordering', description='Order by field', required=False, type=str),
        ],
        responses={200: RedemptionTransactionSerializer(many=True)},
        summary="List all redemption option transactions"
    )
    def get(self, request, *args, **kwargs):
        transactions = RedemptionTransaction.objects.select_related('redemption_option__fooditem').all()

        # Filtering by status
        status_filter = request.query_params.get('status')
        if status_filter:
            transactions = transactions.filter(status=status_filter)

        # Searching by food item name
        search_query = request.query_params.get('search')
        if search_query:
            transactions = transactions.filter(redemption_option__fooditem__name__icontains=search_query)

        # Ordering results (default is by creation date)
        ordering = request.query_params.get('ordering', '-created_at')
        transactions = transactions.order_by(ordering)

        serializer = RedemptionTransactionSerializer(transactions, many=True)
        logger.info(f"Listed redemption transactions for admin {request.user.username}.")
        return Response(serializer.data, status=status.HTTP_200_OK)


class RedemptionTransactionDetailView(APIView):
    """
    Handles retrieval and deletion of a RedemptionTransaction.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        try:
            return RedemptionTransaction.objects.select_related('redemption_option__fooditem').get(pk=pk)
        except RedemptionTransaction.DoesNotExist:
            logger.error(f"Transaction {pk} not found.")
            raise ValidationError("Transaction not found")

    @extend_schema(
        responses={
            200: RedemptionTransactionSerializer,
            404: OpenApiResponse(description="Transaction not found."),
        },
        summary="detail for a redemption option transaction"
    )
    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve a single redemption transaction.
        """
        transaction = self.get_object(pk)
        serializer = RedemptionTransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Transaction deleted."),
            400: OpenApiResponse(description="Cannot delete unless delivered."),
        },
        summary="deletes a redemption option transaction"
    )
    def delete(self, request, pk, *args, **kwargs):
        """
        Delete a transaction if status is delivered.
        """
        transaction = self.get_object(pk)
        if transaction.status == 'DELIVERED':
            transaction.delete()
            logger.info(f"Transaction {pk} deleted by admin {request.user.username}.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        logger.warning(f"Attempt to delete transaction {pk} failed. Status not 'DELIVERED'.")
        return Response({"message": "Cannot delete until delivered."}, status=status.HTTP_400_BAD_REQUEST)


class MarkRedemptionTransactionDeliveredView(APIView):
    """
    Marks a RedemptionTransaction as delivered.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        try:
            return RedemptionTransaction.objects.get(pk=pk)
        except RedemptionTransaction.DoesNotExist:
            logger.error(f"Transaction {pk} not found.")
            raise ValidationError("Transaction not found")

    @extend_schema(
        responses={200: RedemptionTransactionSerializer},
        summary="mark a redemption transaction as delivered"
    )
    def patch(self, request, pk, *args, **kwargs):
        """
        Mark a redemption transaction as delivered. Optionally, the status can be sent in the request body.
        """
        transaction = self.get_object(pk)

        transaction.status = 'DELIVERED'
        transaction.save()

        serializer = RedemptionTransactionSerializer(transaction)
        logger.info(f"Transaction {pk} marked as {status} by admin {request.user.username}.")
        return Response(serializer.data, status=status.HTTP_200_OK)
