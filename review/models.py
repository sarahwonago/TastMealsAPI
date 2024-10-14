import uuid
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

from order.models import Order


class Review(models.Model):
    """
    Model to represent reviews for fooditem.

    Attributes:
        id (UUIDField): Unique identifier for review.
        user(User): the reviewing the order.
        order(Order): the order being reviewed
        rating(PositiveIntegerField):the rating
        comment(TextField): the review text
        created_at (DateTimeField): Timestamp when the review was created.
    """

    class Meta:
        verbose_name_plural = "Reviews"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        related_name="reviews",
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="review")
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Order {self.order.id}"
    