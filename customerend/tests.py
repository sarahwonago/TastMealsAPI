from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()
from customerend.models import CustomerLoyaltyPoint


import unittest

class TestCustomerLoyaltyPoint(unittest.TestCase):

    # Creating a CustomerLoyaltyPoint instance with valid user and points
    def test_create_instance_with_valid_user_and_points(self):
        user = User.objects.create(username='testuser')
        loyalty_point = CustomerLoyaltyPoint.objects.create(user=user, points=100)
        self.assertEqual(loyalty_point.user.username, 'testuser')
        self.assertEqual(loyalty_point.points, 100)

    # Creating a CustomerLoyaltyPoint instance with zero points
    def test_create_instance_with_zero_points(self):
        user = User.objects.create(username='testuser')
        loyalty_point = CustomerLoyaltyPoint.objects.create(user=user, points=0)
        self.assertEqual(loyalty_point.user.username, 'testuser')
        self.assertEqual(loyalty_point.points, 0)