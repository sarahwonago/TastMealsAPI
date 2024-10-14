import uuid
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
from menu.models import FoodItem, SpecialOffer

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
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    def __str__(self):
        return f"{self.user.username}'s cart."
    
        
class CartItem(models.Model):
    """
    Defines an individual item in a cart.

    Attributes:
        id (UUIDField): Unique identifier for the order.
        cart(Cart): cart to store the cartitems.
        fooditem (FoodItem): the fooditem which represents the cartitem
        quantity (PositiveIntegerField): the cartitem quantity
        created_at (DateTimeField): Timestamp when the cartitem was created.
       
    """

    class Meta:
        verbose_name_plural = "Cart Items"
        unique_together = ('cart', 'fooditem')


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart,
        related_name="cartitems",
        on_delete=models.CASCADE
    )
    fooditem = models.ForeignKey(
        FoodItem,
        related_name="cartitems",
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        default = 1,
        help_text="Quantity of the cartitem"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.fooditem.name}"
    
    @property
    def price(self):
        """
        Gets the price of the fooditem dynamically, considering specialoffers.
        """
        price = self.fooditem.price

        # checks if the fooditem has a specialoffer
        try:
            offer= SpecialOffer.objects.get(fooditem=self.fooditem)
            discount = (offer.discount_percentage / 100) * price
            price -= discount
        except SpecialOffer.DoesNotExist:
            pass
      
        return price 
    
    @property
    def total_price(self):
        """
        Calculates the total price of the fooditem dynamically.
        """
        return self.price * self.quantity
        