from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from customerend.models import Cart, CustomerLoyaltyPoint

import logging

logger = logging.getLogger(__name__)

User = get_user_model()

@receiver(post_save, sender=User)
def create_users_cart(sender, instance, created, **kwargs):
    """
    Signal to create cart and loyalty points for users upon creation.

    Creates a cart and loyalty points for customer users upon successful registration.
    """

    if created and instance.role == 'customer':
        # creates customers cart
        Cart.objects.create(user=instance)

        logger.info(f"Cart created for user {instance.username}")

        # creates customers loyalty point
        CustomerLoyaltyPoint.objects.create(user=instance)

        logger.info(f"LoyaltyPoints created for user {instance.username}")
