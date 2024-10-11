from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from .models import Category
from django.contrib.auth import get_user_model
import uuid

class CategoryAPITestCase(APITestCase):
    """
    Unit test case for Category API endpoints.
    """
    
    def setUp(self):
        """
        Setup function to create necessary test data.
        """
        self.client = APIClient()
        self.user_model = get_user_model()

        # Create an admin user for authentication
        self.admin_user = self.user_model.objects.create_user(
            username="adminuser",
            password="adminpass",
            role="cafeadmin"
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create a customer user for negative case tests
        self.customer_user = self.user_model.objects.create_user(
            username="customeruser",
            password="customerpass",
            role="customer"
        )

        # Create some categories for testing
        self.category1 = Category.objects.create(
            name="Snacks",
            description="Snacks and quick bites"
        )
        self.category2 = Category.objects.create(
            name="Desserts",
            description="Sweet desserts"
        )

        # URLs for list and detail endpoints
        self.list_url = reverse('categories-list-create')
        self.detail_url = reverse('category-detail', args=[str(self.category1.id)])

    def test_get_categories(self):
        """
        Test the GET request to fetch all categories.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 2 categories created in setup
        self.assertEqual(response.data[0]["name"], "Snacks")

    def test_create_category(self):
        """
        Test the POST request to create a new category.
        """
        data = {
            "name": "Beverages",
            "description": "Drinks and beverages"
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Beverages")

    def test_create_category_duplicate(self):
        """
        Test POST request for duplicate category name.
        """
        data = {
            "name": "Snacks",  # Duplicate name
            "description": "Test duplicate"
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn("Category 'Snacks' already exists.", response.data["non_field_errors"])

    def test_get_category_detail(self):
        """
        Test the GET request to fetch a single category.
        """
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Snacks")

    def test_update_category(self):
        """
        Test the PUT request to update a category.
        """
        data = {
            "name": "Updated Snacks",
            "description": "Updated description"
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Snacks")

    def test_partial_update_category(self):
        """
        Test the PATCH request to partially update a category.
        """
        data = {"name": "New Snacks"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New Snacks")

    def test_delete_category(self):
        """
        Test the DELETE request to remove a category.
        """
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category1.id).exists())

    def test_permission_for_customer(self):
        """
        Test to ensure only admins can create categories.
        """
        self.client.force_authenticate(user=self.customer_user)
        data = {
            "name": "Fruits",
            "description": "Fresh fruits"
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
