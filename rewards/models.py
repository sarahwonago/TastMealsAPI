import uuid
from django.db import models
from django.contrib.auth import get_user_model
from menu.models import FoodItem

User = get_user_model()


class RedemptionOption(models.Model):
    """
    Defines the model for customerpoints Redemption options.

    Attributes:
        id (UUIDField): Unique identifier for redemptionoption.
        foodItem(foodItem): the fooditem to be redeemed.
        points_required(PositiveIntegerField):points required to redeem this option
        description(TextField): the redemption option brief description
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fooditem = models.OneToOneField(FoodItem, related_name="redeem", on_delete=models.CASCADE)
    points_required = models.PositiveIntegerField()
    description = models.TextField()

    def __str__(self):
        return f"Redeem {self.fooditem.name} for {self.points_required} points"
    


class RedemptionTransaction(models.Model):
    """
    Defines the transaction model for redeeming customerloyaltypoints.

    Attributes:
        id (UUIDField): Unique identifier for redemptiontransaction.
        customer(User): the customer redeeming points.
        redemption_option(RedemptionOption): the redemption option.
        points_redeemed(PositiveIntegerField): the points that have been redeemed
        date(DateTimeField): timestamp when the redemptiontransaction was created
    """

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("DELIVERED", "Delivered"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    redemption_option = models.ForeignKey(RedemptionOption, on_delete=models.SET_NULL, null=True)
    points_redeemed = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=250, default="PENDING", choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer} redeemed {self.points_redeemed} points"