import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from menu.models import FoodItem

User = get_user_model()


class Notification(models.Model):
    """
    Model representing notifications sent to users.
    
    Attributes:
        user (ForeignKey): The user the notification is sent to.
        message (CharField): The notification message.
        is_read (BooleanField): Tracks whether the notification has been read.
        created_at (DateTimeField): When the notification was created.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name_plural = "Notifications"
        ordering = ['-updated_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"



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