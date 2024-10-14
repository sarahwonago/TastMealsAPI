from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Order, CustomerLoyaltyPoint
from cart.models import CartItem, Cart

from cafeadminend.models import Notification, RedemptionOption

from .myutils import award_customer_points

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



@receiver(pre_save, sender=Order)
def order_status_change_notification(sender, instance, **kwargs):
    """
    Send a notification to the customer when the order status changes to 'COMPLETE'.
    """
    # Check if this is an update (instance already exists)
    if instance.pk:
        previous_order = Order.objects.filter(pk=instance.pk).first()
        if previous_order:
            # Check if the status changed to 'COMPLETE'
            if previous_order.status != instance.status and instance.status == "COMPLETE":
                # Notify customer
                Notification.objects.create(
                    user=instance.user,
                    message="Your order has been marked as complete. Please, don't forget to leave a review once you finish dining."
                )


@receiver(pre_save, sender=Order)
def order_payment_notification(sender, instance, **kwargs):
    if instance.pk:
        previous_order = Order.objects.filter(pk=instance.pk).first()
        if previous_order:
            # Check if the is_paid status has changed to True
            if not previous_order.is_paid and instance.is_paid:
                # Notify customer
                Notification.objects.create(
                    user=instance.user,
                    message=f"Your payment for Order was successful. Amount paid: ksh {instance.total_price}"
                )

                # Notify cafe admin
                admins = User.objects.filter(role='cafeadmin')
                for admin in admins:
                    Notification.objects.create(
                        user=admin,
                        message=f"Payment received for Order #{instance.id}. Amount paid: ksh {instance.total_price}"
                    )


@receiver(pre_save, sender=Order)
def award_loyalty_points(sender, instance, **kwargs):
    if instance.pk:
        previous_order = Order.objects.filter(pk=instance.pk).first()
        if previous_order:
            # Check if the is_paid status has changed to True
            if not previous_order.is_paid and instance.is_paid:
                # award loyalty points when order is paid
                award_customer_points(instance)
