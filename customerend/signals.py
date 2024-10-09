from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import CartItem, Cart, Order

from cafeadminend.models import Notification

User = get_user_model()

@receiver(post_save, sender=CartItem)
def update_cart_total_on_save(sender, instance, **kwargs):
    """
    Recalculate the total price of the cart whenever a CartItem is added or updated.
    """
    cart = instance.cart
    cart_total = sum(item.total_price for item in cart.cartitems.all())
    cart.total_price = cart_total
    cart.save()  # Save the updated total to the cart
    print(f"Cart {cart.id} total updated to {cart.total_price}")

@receiver(post_delete, sender=CartItem)
def update_cart_total_on_delete(sender, instance, **kwargs):
    """
    Recalculate the total price of the cart whenever a CartItem is deleted.
    """
    cart = instance.cart
    cart_total = sum(item.total_price for item in cart.cartitems.all())
    cart.total_price = cart_total
    cart.save()  # Save the updated total to the cart
    print(f"Cart {cart.id} total updated to {cart.total_price} after item deletion")



@receiver(post_save, sender=Order)
def notify_user_on_order_update(sender, instance, created, **kwargs):
    """
    Signal that triggers when an Order is updated. 
    If the order status is updated to 'COMPLETE', notify the user.
    """
    if instance.status == 'COMPLETE':
        Notification.objects.create(
            user=instance.user,
            message=f"Your order is now complete. Please dont forget to leave a review."
        )
