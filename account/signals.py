from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from customerend.models import Cart, CustomerLoyaltyPoint

User = get_user_model()

@receiver(post_save, sender=User)
def create_users_cart(sender, instance, created, **kwargs):
    """
    Automatically creates a new cart when a new user is successfully created.
    Automatically creates a new customerloyalty point when a new user is successfully created.
    """

    if created:
        # creates users cart
        Cart.objects.create(user=instance)

        # creates customers loyalty point
        CustomerLoyaltyPoint.objects.create(user=instance)