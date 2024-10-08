from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CartItem, Cart


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
