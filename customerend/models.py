import uuid
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


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
