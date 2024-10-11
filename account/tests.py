from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

User = get_user_model()

class CustomUserTestCase(TestCase):
    """
    Unit tests for Custom User.
    Tests the creation of a custom user with different roles.
    """

    def setUp(self):
        self.customer_user = User.objects.create_user(
            username="customer_user",
            password="testpass123",
            role="customer"
        )
        self.cafeadmin_user = User.objects.create_user(
            username="admin_user",
            password="testpass123",
            role="cafeadmin"
        )

    def test_customer_creation(self):
        """Test that a customer user is created successfully."""
        self.assertEqual(self.customer_user.role, "customer")
        self.assertTrue(self.customer_user.check_password("testpass123"))

    def test_cafeadmin_creation(self):
        """Test that a cafeadmin user is created successfully."""
        self.assertEqual(self.cafeadmin_user.role, "cafeadmin")
        self.assertTrue(self.cafeadmin_user.check_password("testpass123"))



class RoleBasedRedirectAPITestCase(APITestCase):
    """
    Unit tests for role based redirect.
    """

    def setUp(self):
        self.customer_user = User.objects.create_user(
            username="customer_test",
            password="testpass123",
            role="customer"
        )
        self.admin_user = User.objects.create_user(
            username="admin_test",
            password="testpass123",
            role="cafeadmin"
        )

    # def test_customer_redirect(self):
    #     """Test customer user redirection."""
    #     self.client.login(username="customer_test", password="testpass123")
    #     response = self.client.get(reverse('role-based-redirect'))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['role'], 'customer')
    #     self.assertIn('customer-home', response.data['redirect_url'])

    # def test_admin_redirect(self):
    #     """Test admin user redirection."""
    #     self.client.login(username="admin_test", password="testpass123")
    #     response = self.client.get(reverse('role-based-redirect'))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['role'], 'cafeadmin')
    #     self.assertIn('cafeadmin-home', response.data['redirect_url'])



class PermissionsTestCase(APITestCase):
    """
    Unit tests for Permissions.
    """

    def setUp(self):
        self.customer_user = User.objects.create_user(
            username="customer_user",
            password="testpass123",
            role="customer"
        )
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="testpass123",
            role="cafeadmin"
        )

    # def test_admin_permission(self):
    #     """Test that admin has access to admin endpoints."""
    #     self.client.login(username="admin_user", password="testpass123")
    #     response = self.client.get(reverse('cafeadmin-home'))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_customer_permission_denied(self):
    #     """Test that customer user is denied access to admin endpoints."""
    #     self.client.login(username="customer_user", password="testpass123")
    #     response = self.client.get(reverse('cafeadmin-home'))
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
