import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()
from cafeadminend.models import DiningTable, FoodItem, SpecialOffer

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
    