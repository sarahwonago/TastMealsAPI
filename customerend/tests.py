from customerend.models import CustomerLoyaltyPoint
from customerend.models import Transaction
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




class TestTransaction(unittest.TestCase):

    # Creating a Transaction instance with valid data should succeed
    def test_create_transaction_with_valid_data(self):
        user = User.objects.create(username='testuser')
        customer_loyalty_point = CustomerLoyaltyPoint.objects.create(user=user, points=100)
        transaction = Transaction.objects.create(
            customer_loyalty_point=customer_loyalty_point,
            amount=150.00,
            points_earned=15
        )
        self.assertEqual(transaction.customer_loyalty_point, customer_loyalty_point)
        self.assertEqual(transaction.amount, 150.00)
        self.assertEqual(transaction.points_earned, 15)

    # Creating a Transaction with a negative amount should fail
    def test_create_transaction_with_negative_amount(self):
        user = User.objects.create(username='testuser')
        customer_loyalty_point = CustomerLoyaltyPoint.objects.create(user=user, points=100)
        with self.assertRaises(ValueError):
            Transaction.objects.create(
                customer_loyalty_point=customer_loyalty_point,
                amount=-50.00,
                points_earned=0
            )