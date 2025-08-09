"""
Test refactored views to ensure they work correctly with DRF.
"""
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from src.domain.shared.types import WalletId
from src.domain.transactions.entities import Transaction
from src.domain.wallets.entities import Wallet


class TestRefactoredWalletViews(TestCase):
    """Test refactored wallet views with DRF."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.wallet_id = WalletId("123e4567-e89b-12d3-a456-426614174000")
        self.wallet = Wallet(
            id=self.wallet_id,
            label="Test Wallet",
            balance=Decimal("1000"),
            is_active=True,
            deactivated_at=None,
        )

    @patch("src.containers.UseCaseContainer.create_wallet_use_case")
    def test_create_wallet_success(self, mock_use_case):
        """Test successful wallet creation with proper format."""
        # Mock the use case
        mock_use_case_instance = MagicMock()
        mock_use_case_instance.execute.return_value = self.wallet
        mock_use_case.return_value = mock_use_case_instance

        # Test data in proper format (no extra nested data key)
        data = {"data": {"type": "wallets", "attributes": {"label": "Test Wallet"}}}

        # Make request
        response = self.client.post(
            "/api/v1/wallets/create/",
            data=data,
            content_type="application/vnd.api+json",
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["type"], "wallets")
        self.assertEqual(response.data["data"]["attributes"]["label"], "Test Wallet")
        # Balance should be integer in response
        self.assertEqual(response.data["data"]["attributes"]["balance"], 1000)

    def test_create_wallet_invalid_data(self):
        """Test wallet creation with invalid data returns proper error."""
        # Test data missing required fields
        data = {"data": {"type": "wallets", "attributes": {}}}

        # Make request
        response = self.client.post(
            "/api/v1/wallets/create/",
            data=data,
            content_type="application/vnd.api+json",
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ErrorDetail", response.data[0])

    @patch(
        "src.containers.UseCaseContainer.list_wallets_with_database_pagination_use_case"
    )
    def test_list_wallets_success(self, mock_use_case):
        """Test successful wallet listing with proper format."""
        # Mock the use case
        mock_use_case_instance = MagicMock()
        mock_use_case_instance.execute.return_value = {
            "data": [self.wallet],
            "meta": {},
            "links": {},
        }
        mock_use_case.return_value = mock_use_case_instance

        # Make request
        response = self.client.get(
            "/api/v1/wallets/list/", content_type="application/vnd.api+json"
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["type"], "wallets")
        # Balance should be integer in response
        self.assertEqual(response.data["data"][0]["attributes"]["balance"], 1000)

    @patch("src.containers.UseCaseContainer.update_wallet_label_use_case")
    def test_update_wallet_label_success(self, mock_use_case):
        """Test successful wallet label update with proper format."""
        # Mock the use case
        updated_wallet = Wallet(
            id=self.wallet_id,
            label="Updated Label",
            balance=Decimal("1000"),
            is_active=True,
            deactivated_at=None,
        )
        mock_use_case_instance = MagicMock()
        mock_use_case_instance.execute.return_value = updated_wallet
        mock_use_case.return_value = mock_use_case_instance

        # Test data in proper format (no extra nested data key)
        data = {"data": {"type": "wallets", "attributes": {"label": "Updated Label"}}}

        # Make request
        response = self.client.patch(
            f"/api/v1/wallets/{str(self.wallet_id)}/update-label/",
            data=data,
            content_type="application/vnd.api+json",
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["type"], "wallets")
        self.assertEqual(response.data["data"]["attributes"]["label"], "Updated Label")
        # Balance should be integer in response
        self.assertEqual(response.data["data"]["attributes"]["balance"], 1000)

    @patch("src.containers.UseCaseContainer.deactivate_wallet_use_case")
    def test_deactivate_wallet_success(self, mock_use_case):
        """Test successful wallet deactivation with proper format."""
        # Mock the use case
        deactivated_wallet = Wallet(
            id=self.wallet_id,
            label="Test Wallet",
            balance=Decimal("0"),
            is_active=False,
            deactivated_at=None,
        )
        mock_use_case_instance = MagicMock()
        mock_use_case_instance.execute.return_value = deactivated_wallet
        mock_use_case.return_value = mock_use_case_instance

        # Make request
        response = self.client.post(
            f"/api/v1/wallets/{str(self.wallet_id)}/deactivate/",
            content_type="application/vnd.api+json",
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["type"], "wallets")
        self.assertEqual(response.data["data"]["attributes"]["is_active"], False)
        # Balance should be integer in response
        self.assertEqual(response.data["data"]["attributes"]["balance"], 0)


class TestRefactoredTransactionViews(TestCase):
    """Test refactored transaction views with DRF."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.transaction_id = "456e7890-e89b-12d3-a456-426614174001"
        self.wallet_id = "123e4567-e89b-12d3-a456-426614174000"

    @patch("src.containers.UseCaseContainer.create_transaction_use_case")
    def test_create_transaction_success(self, mock_use_case):
        """Test successful transaction creation with proper format."""
        # Mock the use case
        mock_use_case_instance = MagicMock()
        mock_use_case_instance.execute.return_value = Transaction(
            id=self.transaction_id,
            wallet_id=self.wallet_id,
            txid="tx_123456789",
            amount=Decimal("1000"),
            is_active=True,
        )
        mock_use_case.return_value = mock_use_case_instance

        # Test data in proper format
        data = {
            "data": {
                "type": "transactions",
                "attributes": {"wallet_id": self.wallet_id, "amount": "1000"},
            }
        }

        # Make request
        response = self.client.post(
            "/api/v1/transactions/create/",
            data=data,
            content_type="application/vnd.api+json",
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)

        self.assertEqual(response.data["data"]["type"], "transactions")
        self.assertEqual(
            response.data["data"]["attributes"]["wallet_id"], self.wallet_id
        )
        self.assertEqual(response.data["data"]["attributes"]["txid"], "tx_123456789")
        # Amount should be integer in response
        self.assertEqual(response.data["data"]["attributes"]["amount"], 1000)

    def test_create_transaction_invalid_data(self):
        """Test transaction creation with invalid data returns proper error."""
        # Test data missing required fields
        data = {"data": {"type": "transactions", "attributes": {}}}

        # Make request
        response = self.client.post(
            "/api/v1/transactions/create/",
            data=data,
            content_type="application/vnd.api+json",
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ErrorDetail", response.data[0])
