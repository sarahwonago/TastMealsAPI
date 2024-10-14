import logging
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Q

from drf_spectacular.utils import OpenApiParameter, extend_schema, OpenApiExample, OpenApiResponse, inline_serializer


from menu.models import  FoodItem


from .serializers import CartItemSerializer
from .models import Cart, CartItem

from account.permissions import IsCustomer

logger = logging.getLogger(__name__)

class AddItemToCartAPIView(APIView):
    """
    API view to add a FoodItem to the authenticated user's cart.
    
    - POST: Add a food item to the cart.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        request=inline_serializer('CartItemAddRequest', fields={
            'quantity': serializers.IntegerField(default=1, help_text="Quantity of the item to be added to the cart")
        }),
        responses={
            201: CartItemSerializer,
            400: OpenApiResponse(description="Item already added to cart or validation errors"),
            404: OpenApiResponse(description="Food item not found")
        },
        summary="Add an item to the cart",
        description="Adds a specified quantity of a food item to the user's cart. If the item already exists in the cart, it returns an error."
    )
    def post(self, request, fooditem_id, format=None):
        """
        Add an item to the cart for the authenticated user.
        """
        user = request.user
        cart = Cart.objects.get(user=user)
        fooditem = get_object_or_404(FoodItem, id=fooditem_id)

        # Check if the food item is already in the cart
        if CartItem.objects.filter(cart=cart, fooditem=fooditem).exists():
            logger.warning(f"Item {fooditem.name} already in cart for user {user.username}.")
            return Response({"message": "Item already added to cart."}, status=status.HTTP_400_BAD_REQUEST)

        # Handle item addition
        quantity = request.data.get("quantity", 1)
        data = {
            "cart": cart.id,
            "fooditem": fooditem.id,
            "quantity": quantity
        }
        serializer = CartItemSerializer(data=data)

        if serializer.is_valid():
            serializer.save(cart=cart, fooditem=fooditem)
            logger.info(f"Added {fooditem.name} to cart for user {user.username}.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f"Failed to add {fooditem.name} to cart for user {user.username}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartAPIView(APIView):
    """
    API view to retrieve all items in the authenticated user's cart.
    
    - GET: Retrieve all items in the cart.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        responses={
            200: inline_serializer('CartDetailResponse', fields={
                'cart_items': CartItemSerializer(many=True),
                'total_cart_price': serializers.DecimalField(max_digits=10, decimal_places=2)
            })
        },
        summary="Retrieve cart details",
        description="Fetches all items in the user's cart along with the total price."
    )
    def get(self, request, format=None):
        """
        Retrieve all items in the authenticated user's cart.
        """
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)

        serializer = CartItemSerializer(cart_items, many=True)
        return Response({
            "cart_items": serializer.data,
            "total_cart_price": cart.total_price
        }, status=status.HTTP_200_OK)


class CartItemDetailAPIView(APIView):
    """
    API view to update or delete an individual cart item.
    
    - PATCH: Update the quantity of a cart item.
    - DELETE: Remove an item from the cart.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        request=inline_serializer('CartItemUpdateRequest', fields={
            'quantity': serializers.IntegerField(help_text="New quantity for the cart item")
        }),
        responses={
            200: CartItemSerializer,
            400: OpenApiResponse(description="Validation errors or cart item not found"),
        },
        summary="Update cart item",
        description="Updates the quantity of a specific cart item for the user."
    )
    def patch(self, request, cartitem_id, format=None):
        """
        Update the quantity of a cart item.
        """
        cart_item = get_object_or_404(CartItem, id=cartitem_id, cart__user=request.user)
        serializer = CartItemSerializer(cart_item, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            logger.info(f"Updated quantity of {cart_item.fooditem.name} to {cart_item.quantity} for user {request.user.username}.")
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.error(f"Failed to update cart item {cart_item.fooditem.name} for user {request.user.username}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Item removed from cart"),
            404: OpenApiResponse(description="Cart item not found"),
        },
        summary="Delete cart item",
        description="Deletes an item from the user's cart."
    )
    def delete(self, request, cartitem_id, format=None):
        """
        Remove an item from the cart.
        """
        cart_item = get_object_or_404(CartItem, id=cartitem_id, cart__user=request.user)
        cart_item.delete()
        logger.info(f"Deleted {cart_item.fooditem.name} from cart for user {request.user.username}.")
        return Response(status=status.HTTP_204_NO_CONTENT)
