import logging
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework import serializers

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse


from .serializers import OrderSerializer
from .models import Order

from account.permissions import IsCustomer

logger = logging.getLogger(__name__)




class PlaceOrderView(APIView):
    """
    API view to handle placing an order from the user's cart.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        request=None,
        responses={
            201: inline_serializer('OrderResponse', fields={
                'message': serializers.CharField(),
                'order_id': serializers.IntegerField()
            }),
            400: OpenApiResponse(description="No items in cart to place an order.")
        },
        summary="Place an order",
        description="Places an order for the authenticated user from their cart. "
                    "If the cart is empty, returns a 400 error."
    )
    def post(self, request):
        """
        Place an order using the items in the authenticated user's cart.
        
        Returns:
            Response: A JSON response with a success message and order ID.
        """
        user = request.user

        # Fetch user's cart and items
        cart = user.cart
        cart_items = cart.cartitems.all()

        if not cart_items.exists():
            logger.warning("User %s attempted to place an order with an empty cart.", user.username)
            return Response({"message": "The cart is empty, no items to place in the order."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price from the cart items
        total_price = cart.total_price

        # Create the order
        order = Order.objects.create(
            user=user,
            total_price=total_price
        )

        # Add cart items to the order
        # for cart_item in cart_items:
        #     order.order_items.add(cart_item)

        # order.save()

        # Clear the user's cart after the order is placed
        cart.cartitems.all().delete()

        logger.info("Order placed successfully for user %s, order ID: %d.", user.username, order.id)
        return Response({
            "message": "Order placed successfully.",
            "order_id": order.id
        }, status=status.HTTP_201_CREATED)


class OrderListView(APIView):
    """
    API view to retrieve a list of orders for the authenticated user.
    Supports filtering, searching, and ordering of orders.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        parameters=[
            inline_serializer('OrderFilterParams', fields={
                'status': serializers.CharField(required=False, help_text="Filter orders by status."),
                'search': serializers.CharField(required=False, help_text="Search orders by status."),
                'ordering': serializers.CharField(default='-updated_at', help_text="Order by field (e.g. '-updated_at').")
            })
        ],
        responses=OrderSerializer(many=True),
        summary="List user's orders",
        description="Retrieve all orders placed by the authenticated user, with filtering, searching, and ordering capabilities."
    )
    def get(self, request):
        """
        Retrieve a list of orders for the authenticated user.

        Query Parameters:
            - status: Filter orders by status.
            - search: Search for orders by status.
            - ordering: Order the results (default is '-updated_at').
        
        Returns:
            Response: A JSON response with the list of orders.
        """
        # Fetch the orders for the authenticated user
        orders = Order.objects.filter(user=request.user)

        # Filtering by status
        status_param = request.query_params.get('status')
        if status_param:
            orders = orders.filter(status=status_param)

        # Searching by status
        search_param = request.query_params.get('search')
        if search_param:
            orders = orders.filter(status__icontains=search_param)

        # Ordering results
        ordering_param = request.query_params.get('ordering', '-updated_at')
        orders = orders.order_by(ordering_param)

        # Serialize the orders
        serializer = OrderSerializer(orders, many=True)
        logger.info("Fetched %d orders for user %s.", orders.count(), request.user.username)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CancelOrderView(APIView):
    """
    API view to cancel an unpaid order for the authenticated user.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        request=None,
        responses={
            200: inline_serializer('OrderCancelResponse', fields={
                'detail': serializers.CharField(help_text="Cancellation success message.")
            }),
            404: OpenApiResponse(description="Order not found."),
        },
        summary="Cancel an unpaid order",
        description="Cancel an existing unpaid order by order ID."
    )
    def post(self, request, order_id):
        """
        Cancel an unpaid order by ID for the authenticated user.

        Args:
            order_id (int): The ID of the order to cancel.
        
        Returns:
            Response: A success message if the order is cancelled, or a 404 if not found.
        """
        try:
            # Fetch the order
            order = Order.objects.get(id=order_id, user=request.user, is_paid=False)

            # Delete the order
            order.delete()
            logger.info("Order %d cancelled successfully for user %s.", order_id, request.user.username)
            return Response({"detail": "Order cancelled successfully."}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            logger.warning("Attempt to cancel a non-existent order with ID %d by user %s.", order_id, request.user.username)
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )
