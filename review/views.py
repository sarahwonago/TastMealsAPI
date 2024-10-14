from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from .models import Order, Review
from .serializers import ReviewSerializer
from django.utils import timezone
import logging

from account.permissions import IsCustomer

logger = logging.getLogger(__name__)

class AddReviewView(APIView):
    """
    API view to add a review for a fully paid order on the same day.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        request=ReviewSerializer,
        responses={
            201: ReviewSerializer,
            400: OpenApiResponse(description="Bad request, e.g., order already reviewed or not fully paid."),
            404: OpenApiResponse(description="Order not found.")
        },
        summary="Add a review for a fully paid order",
        description="Add a review for a fully paid order. Can only review on the same day the order was paid for."
    )
    def post(self, request, order_id):
        user = request.user
        try:
            # Fetch the order
            order = Order.objects.get(id=order_id, user=user)

            # Check if the order has already been reviewed
            if order.review.exists():
                logger.warning("User %s tried to review order %d, but it is already reviewed.", user.username, order_id)
                return Response({"detail": "Order has already been reviewed. Try updating it."}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure that the order is fully paid
            if not order.is_paid:
                logger.warning("User %s tried to review unpaid order %d.", user.username, order_id)
                return Response({"detail": "You can only review fully paid orders."}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure the review is made on the same day the order was paid for
            if order.updated_at.date() != timezone.now().date():
                logger.warning("User %s tried to review order %d on a different day than it was paid.", user.username, order_id)
                return Response({"detail": "You can only review the order on the same day it was paid."}, status=status.HTTP_400_BAD_REQUEST)

            # Serialize and save the review
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user, order=order)
                logger.info("Review created for order %d by user %s.", order_id, user.username)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            logger.error("Order %d not found for user %s.", order_id, user.username)
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)


class UserReviewsView(APIView):
    """
    API view to list all reviews made by the logged-in user.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        responses={
            200: ReviewSerializer(many=True),
        },
        summary="List user's reviews",
        description="Retrieve a list of all reviews made by the authenticated user."
    )
    def get(self, request):
        reviews = Review.objects.filter(user=request.user)
        serializer = ReviewSerializer(reviews, many=True)
        logger.info("Fetched %d reviews for user %s.", reviews.count(), request.user.username)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateReviewView(APIView):
    """
    API view to update a review on the same day it was created and the order was paid for.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        request=ReviewSerializer,
        responses={
            200: ReviewSerializer,
            400: OpenApiResponse(description="Bad request, e.g., updating review on the wrong day."),
            404: OpenApiResponse(description="Review not found.")
        },
        summary="Update a review",
        description="Update a review on the same day the review was created and the order was paid for."
    )
    def patch(self, request, review_id):
        user = request.user
        try:
            # Fetch the review
            review = Review.objects.get(id=review_id, user=user)

            # Ensure the review can only be updated on the same day the order was paid
            if review.order.updated_at.date() != timezone.now().date():
                logger.warning("User %s tried to update review %d after the allowed date.", user.username, review_id)
                return Response({"detail": "You can only update the review on the same day the order was paid."}, status=status.HTTP_400_BAD_REQUEST)

            # Update the review
            serializer = ReviewSerializer(review, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info("Review %d updated by user %s.", review_id, user.username)
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Review.DoesNotExist:
            logger.error("Review %d not found for user %s.", review_id, user.username)
            return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)


class DeleteReviewView(APIView):
    """
    API view to delete a review.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Review deleted successfully."),
            404: OpenApiResponse(description="Review not found.")
        },
        summary="Delete a review",
        description="Delete a specific review by its ID."
    )
    def delete(self, request, review_id):
        user = request.user
        try:
            # Fetch the review
            review = Review.objects.get(id=review_id, user=user)

            # Delete the review
            review.delete()
            logger.info("Review %d deleted by user %s.", review_id, user.username)
            return Response({"detail": "Review deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        except Review.DoesNotExist:
            logger.error("Review %d not found for user %s.", review_id, user.username)
            return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)
