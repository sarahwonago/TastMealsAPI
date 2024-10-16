from django.test import TestCase

import uuid


import pytest

class TestCart:

    # Creating a Cart instance with a unique UUID
    def test_cart_creation_with_unique_uuid(self):
        from cart.models import Cart
        from django.contrib.auth import get_user_model
        User = get_user_model()
    
        user = User.objects.create(username='testuser', password='password')
        cart = Cart.objects.create(user=user)
    
        assert cart.id is not None
        assert isinstance(cart.id, uuid.UUID)

    # Attempting to create a Cart without a User
    def test_cart_creation_without_user(self):
        from cart.models import Cart
        from django.db.utils import IntegrityError
        import pytest
    
        with pytest.raises(IntegrityError):
            Cart.objects.create()