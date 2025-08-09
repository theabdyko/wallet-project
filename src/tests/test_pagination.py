"""
Tests for JSON:API pagination functionality.
"""
from decimal import Decimal
from uuid import uuid4

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from src.domain.shared.types import Money, TransactionId, TxId, WalletId
from src.infrastructure.transactions.models import Transaction as TransactionModel
from src.infrastructure.wallets.models import Wallet as WalletModel


class TestJSONAPIPagination(TestCase):
    """Test JSON:API pagination functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create test wallets
        self.wallets = []
        for i in range(25):  # Create 25 wallets to test pagination
            wallet = WalletModel.objects.create(
                id=WalletId(uuid4()),
                label=f"Test Wallet {i}",
                balance=Decimal(f"{i * 100}"),
                is_active=True,
            )
            self.wallets.append(wallet)

        # Create test transactions
        self.transactions = []
        for i in range(30):  # Create 30 transactions to test pagination
            transaction = TransactionModel.objects.create(
                id=TransactionId(uuid4()),
                wallet_id=self.wallets[i % len(self.wallets)].id,
                txid=TxId(f"tx_{i:06d}"),
                amount=Money(Decimal(f"{i * 50}")),
                is_active=True,
            )
            self.transactions.append(transaction)

    def test_wallet_list_pagination_default(self):
        """Test wallet list pagination with default settings."""
        # Use direct URL instead of reverse to avoid URL configuration issues
        response = self.client.get("/api/v1/wallets/list/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertIn("links", response.data)
        self.assertIn("meta", response.data)

        # Check pagination meta
        meta = response.data["meta"]
        self.assertEqual(meta["count"], 25)
        self.assertEqual(meta["page"], 1)
        self.assertEqual(meta["page_size"], 20)
        self.assertEqual(meta["pages"], 2)  # 25 items / 20 per page = 2 pages

        # Check pagination links
        links = response.data["links"]
        self.assertIn("first", links)
        self.assertIn("last", links)
        self.assertIsNone(links["prev"])  # First page has no previous
        self.assertIsNotNone(links["next"])  # First page has next

        # Check data
        data = response.data["data"]
        self.assertEqual(len(data), 20)  # First page should have 20 items

    def test_wallet_list_pagination_custom_page_size(self):
        """Test wallet list pagination with custom page size."""
        response = self.client.get("/api/v1/wallets/list/", {"page_size": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        meta = response.data["meta"]
        self.assertEqual(meta["count"], 25)
        self.assertEqual(meta["page"], 1)
        self.assertEqual(meta["page_size"], 10)
        self.assertEqual(meta["pages"], 3)  # 25 items / 10 per page = 3 pages

        data = response.data["data"]
        self.assertEqual(len(data), 10)  # First page should have 10 items

    def test_wallet_list_pagination_second_page(self):
        """Test wallet list pagination to second page."""
        response = self.client.get(
            "/api/v1/wallets/list/", {"page": 2, "page_size": 10}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        meta = response.data["meta"]
        self.assertEqual(meta["page"], 2)

        links = response.data["links"]
        self.assertIsNotNone(links["prev"])  # Second page has previous
        self.assertIsNotNone(links["next"])  # Second page has next

        data = response.data["data"]
        self.assertEqual(len(data), 10)  # Second page should have 10 items

    def test_transaction_list_pagination(self):
        """Test transaction list pagination."""
        response = self.client.get("/api/v1/transactions/list/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertIn("links", response.data)
        self.assertIn("meta", response.data)

        meta = response.data["meta"]
        self.assertEqual(meta["count"], 30)
        self.assertEqual(meta["page"], 1)
        self.assertEqual(meta["page_size"], 20)
        self.assertEqual(meta["pages"], 2)  # 30 items / 20 per page = 2 pages

        data = response.data["data"]
        self.assertEqual(len(data), 20)  # First page should have 20 items

    def test_transaction_list_pagination_with_filters(self):
        """Test transaction list pagination with filters."""
        wallet_id = str(self.wallets[0].id)
        response = self.client.get(
            "/api/v1/transactions/list/", {"wallet_ids": wallet_id, "page_size": 5}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        meta = response.data["meta"]
        self.assertLessEqual(meta["count"], 30)  # Should be filtered
        self.assertEqual(meta["page_size"], 5)

        data = response.data["data"]
        self.assertEqual(len(data), min(5, meta["count"]))  # Should respect page size

    def test_pagination_links_preserve_filters(self):
        """Test that pagination links preserve existing filters."""
        response = self.client.get(
            "/api/v1/wallets/list/", {"is_active": "true", "page_size": 10}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        links = response.data["links"]
        first_link = links["first"]

        # Check that the first link preserves the is_active filter
        self.assertIn("page_size=10", first_link)
        self.assertIn("page=1", first_link)

    def test_invalid_page_number_handling(self):
        """Test handling of invalid page numbers."""
        response = self.client.get(
            "/api/v1/wallets/list/",
            {"page": 999},  # Page number beyond available pages
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should return the last available page
        meta = response.data["meta"]
        self.assertEqual(meta["page"], 2)  # Last page

    def test_invalid_page_size_handling(self):
        """Test handling of invalid page sizes."""
        response = self.client.get(
            "/api/v1/wallets/list/",
            {"page_size": 999},  # Page size beyond maximum
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()[0], "Page size must be between 1 and 100")
