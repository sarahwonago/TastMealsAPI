from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from customerend.models import Cart

User = get_user_model()

@receiver(post_save, sender=User)
def create_users_cart(sender, instance, created, **kwargs):
    """
    Automatically creates a new cart when a new user is successfully created.
    """

    if created:
        Cart.objects.create(user=instance)