import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    """
    Model representing a category for food items.

    Attributes:
        id (UUIDField): The unique identifier for the category.
        name (CharField): The name of the category.
        description (TextField): A brief description of the category.
        created_at (DateTimeField): The timestamp when the category was created.
        updated_at (DateTimeField): The timestamp when the category was last updated.
    """

    class Meta:
        verbose_name_plural = "Categories"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    """
    Model representing a fooditem.

    Attributes:
        id (UUIDField): The unique identifier for the fooditem.
        category (ForeignKey): The category in which the fooditem belongs to.
        name (CharField): The name of the fooditem.
        price (DecimalField): The price of the fooditem.
        image (ImageField) :The imageof the fooditem.
        description (TextField): Brief description for the fooditem.
        created_at (DateTimeField): Timestamp when the fooditem was created.
        updated_at (DateTimeField): Timestamp when the fooditem was updated.
        is_available (BooleanField): Availability of the fooditem.

    """

    class Meta:
        verbose_name_plural = "FoodItems"
        

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        Category,
        related_name="fooditems",
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=250, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to="food_images/", default="food_images/default.jpg")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField("Availability", default=True)

    def __str__(self):
        return self.name


class DiningTable(models.Model):
    """
    Model representing a dinningtable.

    Attributes:
        id (UUIDField): The unique identifier for the dinningtable
        table_number (PositiveIntegerField)- represents the table number
        created_at (DateTimeField): Timestamp when the dinningtable was created.
        updated_at (DateTimeField): Timestamp when the dinningtable was updated.
    """


    class Meta:
        verbose_name_plural = "Dining Tables"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    table_number = models.PositiveIntegerField(verbose_name="Table Number", unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table {self.table_number}"
    

class SpecialOffer(models.Model):
    """
    Defines a specialoffer that can be applied to a fooditem.

    Attributes:
        id (UUIDField): Unique identifier for the special offer.
        name (CharField): The name of the special offer (e.g., Christmas, Easter).
        fooditem (OneToOneField): The food item that the offer applies to.
        discount_percentage (DecimalField): The percentage discount offered.
        start_date (DateTimeField): When the offer starts.
        end_date (DateTimeField): When the offer ends.
        description (TextField): Additional details about the offer.
    """

    class Meta:
        verbose_name_plural = "SpecialOffers"

    OFFER_CHOICES = (
        ('CHRISTMAS','Christmas'),
        ('BOXING DAY', 'Boxing Day'),
        ('EASTER', 'Easter')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, choices=OFFER_CHOICES, default="Christmas")
    fooditem = models.OneToOneField(
        FoodItem,
        related_name="specialoffer",
        on_delete=models.CASCADE
    )
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 20.00 for 20%
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)

    @property
    def is_active(self):
        """
        Checks if the offer is currently active based on the current date.
        """
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    @property
    def price(self):
        """
        Actual price for the fooditem on offer
        """
        return self.fooditem.price

    def __str__(self):
        return f"{self.name} - {self.discount_percentage}% Off for {self.fooditem.name}"
    


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



