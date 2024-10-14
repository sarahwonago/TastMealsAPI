import uuid
from django.db import models
from django.contrib.auth import get_user_model

from order.models import Order

User = get_user_model()

# Create your models here.
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
