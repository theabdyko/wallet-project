"""
Basic tests to verify the test setup is working correctly.
"""
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class BasicTestSetup(TestCase):
    """Basic test to verify the test setup is working."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

    def test_api_docs_endpoint(self):
        """Test that the API docs endpoint is accessible."""
        response = self.client.get("/docs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wallet_list_endpoint_exists(self):
        """Test that the wallet list endpoint exists."""
        response = self.client.get("/api/v1/wallets/list/")
        # Should not be 404 (endpoint exists)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_transaction_list_endpoint_exists(self):
        """Test that the transaction list endpoint exists."""
        response = self.client.get("/api/v1/transactions/list/")
        # Should not be 404 (endpoint exists)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
