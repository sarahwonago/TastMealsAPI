import logging
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework import serializers


from order.models import Order
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from dinning.models import DiningTable

from account.permissions import IsCustomer

logger = logging.getLogger(__name__)

class PaymentView(APIView):
    """
    API view to handle payments using Daraja API (M-Pesa).
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        request=inline_serializer(
            name="PaymentRequest",
            fields={
                'dining_table': serializers.IntegerField(help_text="ID of the dining table for the order.")
            }
        ),
        responses={
            200: inline_serializer(
                name="PaymentSuccessResponse",
                fields={
                    "detail": serializers.CharField(help_text="Success message after payment.")
                }
            ),
            400: OpenApiResponse(description="Bad request due to invalid inputs."),
            404: OpenApiResponse(description="Order or Dining Table not found.")
        },
        summary="Initiate order payment",
        description="Handles the payment for an order using M-Pesa via the Daraja API. "
                    "Also assigns a dining table to the order."
    )
    def post(self, request, order_id):
        """
        Initiate payment for a given order and assign a dining table.
        
        Args:
            - order_id: ID of the order to be paid.
        
        Returns:
            - Success message with status 200 if payment is successful.
            - Error message with appropriate status code for failures.
        """
        user = request.user
        try:
            # Fetch the order for the authenticated user
            order = Order.objects.get(id=order_id, user=user)

            # Check if the order is already paid
            if order.is_paid:
                logger.warning("User %s attempted to pay for an already paid order %d.", user.username, order_id)
                return Response({"detail": "Order is already paid."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the dining table from the request data
            dining_table_id = request.data.get('dining_table')
            if not dining_table_id:
                logger.error("No dining table ID provided for order %d.", order_id)
                return Response({"detail": "Dining table ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                dining_table = DiningTable.objects.get(id=dining_table_id)
            except DiningTable.DoesNotExist:
                logger.error("Dining table with ID %d not found for order %d.", dining_table_id, order_id)
                return Response({"detail": "Dining table not found."}, status=status.HTTP_404_NOT_FOUND)

            # Payment process (Daraja API logic) would be integrated here.
            amount = order.total_price

            # Example: Daraja API payment logic goes here
            # response = daraja_api.initiate_payment(amount=amount, phone_number=user.phone_number)
            # Handle Daraja response and check for success

            # Assuming payment is successful, update the order
            order.dining_table = dining_table
            order.is_paid = True
            order.save()

            logger.info("Payment successful for order %d by user %s.", order_id, user.username)
            return Response({"detail": "Payment successful. Order updated."}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            logger.error("Order with ID %d not found for user %s.", order_id, user.username)
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
