import logging
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from rest_framework.exceptions import ValidationError

from cafeadminend.models import Category, DiningTable, FoodItem, SpecialOffer
from cafeadminend.serializers import (CategorySerializer, DiningTableSerializer, FoodItemSerializer, SpecialOfferSerializer)

from .serializers import CartItemSerializer
from .models import CartItem, Cart

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
    

class CategoryListCreateAPIView(APIView):
    """
    API view to retrieve list of all categories.

    - GET: Returns a list of all categories with filtering, searching, and ordering.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

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


    # Cache the list of categories for 5 minutes
    @method_decorator(cache_page(60 * 5))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class CategoryDetailAPIView(APIView):
    """
    API view to retrieve a category.

    - GET: Retrieves details of a category by ID.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

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
        
        fooditems = FoodItem.objects.filter(category=category)
        #serializer = CategorySerializer(category)
        serializer = FoodItemSerializer(fooditems, many=True)
        logger.debug(f"Fetched details for category with ID {pk}")

        # modify to include fooditems under this category
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Cache the category detail for 5 minutes
    @method_decorator(cache_page(60 * 5))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
   

class DiningTableListAPIView(APIView):
    """
    API view to retrieve dining tables.
    
    - GET: List all dining tables (with filtering, searching, and ordering).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        List all dining tables with filtering, searching, and ordering.
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
    


class AddItemToCartAPIView(APIView):
    """
    API view to add an item to the cart.
    """

    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request, fooditem_id, format=None):
        """
        Add an item to the cart for the authenticated user.
        """
        user = request.user
        # gets users cart
        cart = Cart.objects.get(user=user)

        fooditem = get_object_or_404(FoodItem, id=fooditem_id)

        # checks if fooditem is already added to cart
        try:
            cart_item =CartItem.objects.get(cart=cart, fooditem=fooditem)
            if cart_item:
                return Response({"message":"Item already added to cart."}, status=status.HTTP_400_BAD_REQUEST)
        except CartItem.DoesNotExist:
            pass

        quantity =request.data.get("quantity", 1)
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
        logger.error(f"Failed to add {fooditem.name} to cart: {serializer.errors}.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class CartAPIView(APIView):
    """
    API view to retrieve all items in the cart.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request, format=None):
        """
        Retrieve all items in the authenticated user's cart.
        """
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)

        serializer = CartItemSerializer(cart_items, many=True)
        total_cart_price = sum(item.total_price for item in cart_items)

        return Response({
            "cart_items": serializer.data,
            "total_cart_price": cart.total_price
        }, status=status.HTTP_200_OK)


class CartItemDetailAPIView(APIView):
    """
    API view to update or delete an individual cart item.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def patch(self, request, cartitem_id, format=None):
        """
        Update the quantity of a cart item.
        """
        cart_item = get_object_or_404(CartItem, id=cartitem_id, cart__user=request.user)

        serializer = CartItemSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Updated quantity of {cart_item.fooditem.name} to {cart_item.quantity}.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Failed to update cart item: {serializer.errors}.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, cartitem_id, format=None):
        """
        Remove an item from the cart.
        """
        cart_item = get_object_or_404(CartItem, id=cartitem_id, cart__user=request.user)
        cart_item.delete()
        logger.info(f"Deleted {cart_item.fooditem.name} from cart.")
        return Response(status=status.HTTP_204_NO_CONTENT)
