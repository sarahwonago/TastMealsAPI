import logging
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Q

from drf_spectacular.utils import OpenApiParameter, extend_schema, OpenApiExample


from cafeadminend.models import  Notification, RedemptionOption, RedemptionTransaction
from menu.models import Category, FoodItem, SpecialOffer, DiningTable
from cafeadminend.serializers import (NotificationSerializer, RedemptionOptionSerializer)

from menu.serializers import (CategorySerializer, DiningTableSerializer, FoodItemSerializer, SpecialOfferSerializer)
from .serializers import CartItemSerializer, OrderSerializer, ReviewSerializer, CustomerLoyaltyPointSerializer
from .models import CartItem, Cart, Order, Review, CustomerLoyaltyPoint

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
    

class CategoryListAPIView(APIView):
    """
    API view to retrieve list of all categories.

    - GET: Returns a list of all categories with filtering, searching, and ordering.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

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


class DiningTableListAPIView(APIView):
    """
    API view to retrieve dining tables.
    
    - GET: List all dining tables (with filtering, searching, and ordering).
    """
    permission_classes = [IsAuthenticated]

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


class PlaceOrderView(APIView):
    """
    Handles creating an order.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request, *args, **kwargs):
        """
        Endpoint for placing an order from the user's cart.
        """
        user = request.user
        # fetching users cartitems
        cart = user.cart
        cart_items = cart.cartitems.all()
        
        if not cart_items.exists():
            return Response({"message":"The cart is empty, no items to place in the order."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price from the users cart
        total_price = cart.total_price

        # Create the order
        order = Order.objects.create(
            user=user,
            total_price=total_price
        )
        
        # Add cart items to the order
        order.order_items.set(cart_items)
        order.save()
        
        # Clear the user's cart after the order is placed
        cart.cartitems.all().delete()
        cart.save()

        return Response({
            "message": "Order placed successfully.",
            "order_id": order.id
        }, status=status.HTTP_201_CREATED)
        

class OrderListView(APIView):
    """
    API view to retrieve a list of orders for the authenticated user,
    with filtering, ordering, and searching capabilities.
    """

    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        """
        Retrieve a list of orders for the authenticated user.
        Allows filtering, searching, and ordering.
        """
        # Fetch the orders for the authenticated user
        orders = Order.objects.filter(user=request.user)

        # Filtering
        status_param = request.query_params.get('status', None)

        if status_param:
            orders = orders.filter(status=status_param)

        # Searching
        search_param = request.query_params.get('search', None)
        if search_param:
            orders = orders.filter(status__icontains=search_param)

        # Ordering
        ordering_param = request.query_params.get('ordering', '-updated_at')
        orders = orders.order_by(ordering_param)

        # Serialize the orders
        serializer = OrderSerializer(orders, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class CancelOrderView(APIView):
    """
    API view to cancel an existing unpaid order.
    """

    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request, order_id):
        """
        Cancel an unpaid order by ID for the authenticated user.
        """
        try:
            # Fetch the order
            order = Order.objects.get(id=order_id, user=request.user, is_paid=False)

            # delete the order
            order.delete()
            return Response({"detail": "Order cancelled successfully."}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )



class PaymentView(APIView):
    """
    API view to handle payments using Daraja API (M-Pesa).

    Attributes:
        permission_classes (list): Only authenticated users can access this view.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        """
        Post method to initiate payment for an order.
        """
        user = request.user
        try:
            order = Order.objects.get(id=order_id, user=user)

            # Check if order is already paid
            if order.is_paid:
                return Response({"detail": "Order is already paid."}, status=status.HTTP_400_BAD_REQUEST)

            # Payment amount will be the total price of the order
            amount = order.total_price

            # Get the dining table from request body
            dining_table_id = request.data.get('dining_table')
            if dining_table_id:
                try:
                    dining_table = DiningTable.objects.get(id=dining_table_id)
                except DiningTable.DoesNotExist:
                    return Response({"detail": "Dining table not found."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"detail": "Dining table ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Daraja API integration logic here
            

            # Update order with dining table and mark as paid
            order.dining_table = dining_table
            order.is_paid = True
            order.save()
                

            return Response({"detail": "Payment successful. Order updated."}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    

class AddReviewView(APIView):
    """
    API view to add a review for a fully paid order on the same day.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request, order_id):
        user = request.user
        try:
            order = Order.objects.get(id=order_id, user=user)

            # checks if the order has already been reviewed
            if order.review:
                return Response({"detail": "Order has alreeady been reviewed. Try updating it."}, status=status.HTTP_400_BAD_REQUEST)


            # Ensure that the order is fully paid
            if not order.is_paid:
                return Response({"detail": "You can only review fully paid orders."}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure that the review is made on the same day the order was paid for
            if order.updated_at.date() != timezone.now().date():
                return Response({"detail": "You can only review the order on the same day it was paid."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user, order=order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)


class UserReviewsView(APIView):
    """
    API view to list all reviews made by the logged-in user.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        reviews = Review.objects.filter(user=request.user)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateReviewView(APIView):
    """
    API view to update a review on the same day it was created and the order was paid for.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def patch(self, request, review_id):
        user = request.user
        try:
            review = Review.objects.get(id=review_id, user=user)

            if review.order.updated_at.date() != timezone.now().date():
                return Response({"detail": "You can only update the review on the same day the order was paid."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ReviewSerializer(review, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Review.DoesNotExist:
            return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)


class DeleteReviewView(APIView):
    """
    API view to delete a review.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def delete(self, request, review_id):
        user = request.user
        try:
            review = Review.objects.get(id=review_id, user=user)
            review.delete()
            return Response({"detail": "Review deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        except Review.DoesNotExist:
            return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)


class NotificationListView(APIView):
    """
    View to list all notifications for the authenticated user with filtering, searching, and ordering.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

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
    permission_classes = [IsAuthenticated, IsCustomer]

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
    permission_classes = [IsAuthenticated, IsCustomer]

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
    permission_classes = [IsAuthenticated, IsCustomer]

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


class CustomerLoyaltyPointView(APIView):
    """
    Endpoint to view customer loyalty points.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        try:
            customer_points = CustomerLoyaltyPoint.objects.get(user=request.user)
            serializer = CustomerLoyaltyPointSerializer(customer_points)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomerLoyaltyPoint.DoesNotExist:
            return Response({"detail": "Loyalty points not found."}, status=status.HTTP_404_NOT_FOUND)
        
class RedemptionOptionListView(APIView):
    """
    Handles the creation and listing of RedemptionOptions using APIView.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

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

class RedeemLoyaltyPointsAPIView(APIView):
    """
    Endpoint to redeem customer loyalty points.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request,redemption_id, *args, **kwargs):
        redemption_option = RedemptionOption.objects.get(id=redemption_id)
        points_required = redemption_option.points_required
        user = request.user

        # Check if user has enough points
        if user.customerloyaltypoint.points < points_required:
            return Response({"message":"You don't have enough points to redeem this option."},status=status.HTTP_400_BAD_REQUEST)

        # Deduct points
        user.customerloyaltypoint.points -= points_required
        user.customerloyaltypoint.save()

        # Create Redemption Transaction
        transaction = RedemptionTransaction.objects.create(
            customer=user,
            redemption_option=redemption_option,
            points_redeemed=points_required,
        )

        # send notification to user
        Notification.objects.create(
            user=user,
            message=f"You have redeemed {points_required} for {redemption_option.fooditem}. Go pick it up at the counter",

        )
        
        
        return Response({"message":f"Successfully redeemed {points_required}. points"}, status=status.HTTP_201_CREATED)