import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()
from menu.models import DiningTable
from cart.models import CartItem

class Order(models.Model):
    """
    Defines an Order.

    Attributes:
        id (UUIDField): Unique identifier for the order.
        user(User): the user to whom the order belongs to.
        order_items(CartItem): cartitems 
        total_price (DecimalField): the total price for the order
        is_paid (BooleanField): indicates if an order has been paid for.
        estimated_time (IntegerField): estimated delivery time for the order
        status (CharField): the order status
        created_at (DateTimeField): Timestamp when the order was created.
        updated_at (DateTimeField): Timestamp when the order was updated.
    """

    class Meta:
        verbose_name_plural = "Orders"
        ordering = ['-updated_at']

    
    ESTIMATED_TIME_CHOICES = [(i, f"{i} minutes") for i in range(5, 65, 5)]
    STATUS_CHOICES = (
        ("COMPLETE", "Complete"),
        ("PENDING", "Pending"),
        ("READY", "Ready for delivery"),
        ("DELIVERED", "Delivered"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        related_name="orders",
        on_delete=models.CASCADE
    )
    order_items = models.ManyToManyField(CartItem)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    estimated_time = models.IntegerField(
        "Estimated Delivery Time",
        choices=ESTIMATED_TIME_CHOICES,
        default=5
    )
    dining_table = models.ForeignKey(DiningTable, max_length=250, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=250, default="PENDING", choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order for - {self.user.username} at: {self.dining_table}"
    
    @property
    def can_review(self):
        """
        Validates if the user can review an order the same day they paid for it.
        """
        return self.updated_at.date() == timezone.now().date()
    

class Payment(models.Model):
    """
    Defines a Payment model to track the payments made by the customer.

    Attributes:
        id (UUIDField): Unique identifier for the payment.
        order (ForeignKey): The order associated with the payment.
        user (ForeignKey): The user who made the payment.
        amount (DecimalField): The amount paid.
        transaction_id (CharField): The M-Pesa transaction ID.
        status (CharField): Status of the payment (Pending, Completed, Failed).
        created_at (DateTimeField): When the payment was created.
    """
   

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, related_name='payments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} for Order {self.order.id} by {self.user.username}"


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
    
class CustomerLoyaltyPoint(models.Model):
    """
    Model to track customer loyalty points.

    Attributes:
        id (UUIDField): Unique identifier for customerloyaltypoint.
        user(User): the user to whom the points belong to.
        points(PositiveIntegerField):points awarded

    """
    
    class Meta:
        verbose_name_plural = "CustomerLoyaltyPoints"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customerloyaltypoint")
    points = models. PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user.username} has {self.points} points"

class Transaction(models.Model):
    """
    Defines the transaction for the points awarded to the user.

    Attributes:
        id (UUIDField): Unique identifier for transaction.
        customer_point(CustomerLoyaltyPoint): the customerpoint instance.
        amount(DecimalField): the order total 
        points_earned(PositiveIntegerField):points awarded based on the order total
        date(DateTimeField): timestamp when the transaction was created
    """

    class Meta:
        verbose_name_plural = "Transaction"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_loyalty_point = models.ForeignKey(CustomerLoyaltyPoint, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2) # order total 
    points_earned = models.PositiveIntegerField() # points awarded based on the order total
    date_awarded = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.points_earned} points awarded on {self.date_awarded.date()}"
