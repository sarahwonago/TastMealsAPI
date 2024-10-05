import uuid
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Cart(models.Model):
    """
    Defines a Cart.

    Attributes:
        id (UUIDField): Unique identifier for the cart.
        user(ForeignKey): the user to whom the cart belongs to.
    """

    class Meta:
        verbose_name_plural = "Carts"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        related_name="cart",
        on_delete=models.CASCADE
    )


    def __str__(self):
        return f"{self.user.username}'s cart."
    
    @property
    def total_price(self):
        """
        Dynamically Calculates the total price based on the cartitems.
        """
        return sum(item.total_price for item in self.cartitems.all())
        
