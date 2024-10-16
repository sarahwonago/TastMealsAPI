import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()
from dinning.models import DiningTable
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
    #order_items = models.ManyToManyField(CartItem)
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
        return f"Order for - {self.user}"
    
    @property
    def can_review(self):
        """
        Validates if the user can review an order the same day they paid for it.
        """
        return self.updated_at.date() == timezone.now().date()
    
