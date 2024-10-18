
from cart.models import Cart
from django.contrib.auth import get_user_model

User = get_user_model()

import unittest

class TestCart(unittest.TestCase):

    # Creating a Cart instance with a valid user and default total_price
    def test_create_cart_with_valid_user(self):
        user = User.objects.create(username='testuser')
        cart = Cart.objects.create(user=user)
        self.assertEqual(cart.user, user)
        self.assertEqual(cart.total_price, 0.00)

    # Attempting to create a Cart without a user
    def test_create_cart_without_user(self):
        with self.assertRaises(ValueError):
            Cart.objects.create()