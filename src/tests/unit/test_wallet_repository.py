"""
Unit tests for wallet repository filtering functionality.

These tests verify the repository layer filtering logic without
database interaction, using mocked Django models.
"""
# Standard library imports
from decimal import Decimal
from unittest.mock import Mock, patch

# Third-party imports
import pytest
from django.db.models import QuerySet

from src.domain.shared.types import WalletId
from src.domain.wallets.entities import Wallet

# Local imports
from src.infrastructure.wallets.repositories import DjangoWalletRepository


class TestDjangoWalletRepository:
    """Test Django wallet repository filtering functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.repository = DjangoWalletRepository()

        # Create test wallet IDs
        self.wallet_id_1 = WalletId("123e4567-e89b-12d3-a456-426614174000")
        self.wallet_id_2 = WalletId("456e7890-e89b-12d3-a456-426614174001")
        self.wallet_id_3 = WalletId("789e0123-e89b-12d3-a456-426614174002")

        # Create test wallets
        self.wallet_1 = Wallet(
            id=self.wallet_id_1,
            label="Test Wallet 1",
            balance=Decimal("1000"),
            is_active=True,
        )
        self.wallet_2 = Wallet(
            id=self.wallet_id_2,
            label="Test Wallet 2",
            balance=Decimal("2000"),
            is_active=False,
        )
        self.wallet_3 = Wallet(
            id=self.wallet_id_3,
            label="Test Wallet 3",
            balance=Decimal("3000"),
            is_active=True,
        )

    @patch("src.infrastructure.wallets.repositories.WalletModel.objects")
    def test_filter_wallets_no_filters_returns_all(self, mock_objects):
        """Test filtering with no filters returns all wallets."""
        # Arrange
        mock_queryset = Mock(spec=QuerySet)
        mock_objects.all.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = [
            Mock(
                id=self.wallet_id_1,
                label="Test Wallet 1",
                balance=Decimal("1000"),
                is_active=True,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
            Mock(
                id=self.wallet_id_2,
                label="Test Wallet 2",
                balance=Decimal("2000"),
                is_active=False,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
            Mock(
                id=self.wallet_id_3,
                label="Test Wallet 3",
                balance=Decimal("3000"),
                is_active=True,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
        ]

        # Act
        result = self.repository.filter_wallets()

        # Assert
        assert len(result) == 3
        mock_objects.all.assert_called_once()
        mock_queryset.filter.assert_not_called()
        # order_by is now called in _build_filter_queryset with default ordering
        mock_queryset.order_by.assert_called_once_with("-balance")

    @patch("src.infrastructure.wallets.repositories.WalletModel.objects")
    def test_filter_wallets_only_is_active_true(self, mock_objects):
        """Test filtering with only is_active=True filter."""
        # Arrange
        mock_queryset = Mock(spec=QuerySet)
        mock_objects.all.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = [
            Mock(
                id=self.wallet_id_1,
                label="Test Wallet 1",
                balance=Decimal("1000"),
                is_active=True,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
            Mock(
                id=self.wallet_id_3,
                label="Test Wallet 3",
                balance=Decimal("3000"),
                is_active=True,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
        ]

        # Act
        result = self.repository.filter_wallets(is_active=True)

        # Assert
        assert len(result) == 2
        mock_queryset.filter.assert_called_once_with(is_active=True)
        # order_by is now called in _build_filter_queryset with default ordering
        mock_queryset.order_by.assert_called_once_with("-balance")

    @patch("src.infrastructure.wallets.repositories.WalletModel.objects")
    def test_filter_wallets_only_is_active_false(self, mock_objects):
        """Test filtering with only is_active=False filter."""
        # Arrange
        mock_queryset = Mock(spec=QuerySet)
        mock_objects.all.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = [
            Mock(
                id=self.wallet_id_2,
                label="Test Wallet 2",
                balance=Decimal("2000"),
                is_active=False,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            )
        ]

        # Act
        result = self.repository.filter_wallets(is_active=False)

        # Assert
        assert len(result) == 1
        mock_queryset.filter.assert_called_once_with(is_active=False)
        # order_by is now called in _build_filter_queryset with default ordering
        mock_queryset.order_by.assert_called_once_with("-balance")

    @patch("src.infrastructure.wallets.repositories.WalletModel.objects")
    def test_filter_wallets_only_wallet_ids(self, mock_objects):
        """Test filtering with only wallet_ids filter."""
        # Arrange
        mock_queryset = Mock(spec=QuerySet)
        mock_objects.all.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = [
            Mock(
                id=self.wallet_id_1,
                label="Test Wallet 1",
                balance=Decimal("1000"),
                is_active=True,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
            Mock(
                id=self.wallet_id_2,
                label="Test Wallet 2",
                balance=Decimal("2000"),
                is_active=False,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
        ]

        wallet_ids = [self.wallet_id_1, self.wallet_id_2]

        # Act
        result = self.repository.filter_wallets(wallet_ids=wallet_ids)

        # Assert
        assert len(result) == 2
        mock_queryset.filter.assert_called_once_with(
            id__in=[self.wallet_id_1, self.wallet_id_2]
        )
        # order_by is now called in _build_filter_queryset with default ordering
        mock_queryset.order_by.assert_called_once_with("-balance")

    @patch("src.infrastructure.wallets.repositories.WalletModel.objects")
    def test_filter_wallets_both_filters_together(self, mock_objects):
        """Test filtering with both is_active and wallet_ids filters."""
        # Arrange
        mock_queryset = Mock(spec=QuerySet)
        mock_objects.all.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = [
            Mock(
                id=self.wallet_id_1,
                label="Test Wallet 1",
                balance=Decimal("1000"),
                is_active=True,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            )
        ]

        wallet_ids = [self.wallet_id_1, self.wallet_id_3]

        # Act
        result = self.repository.filter_wallets(is_active=True, wallet_ids=wallet_ids)

        # Assert
        assert len(result) == 1
        # Should call filter twice: once for is_active, once for wallet_ids
        assert mock_queryset.filter.call_count == 2
        # order_by is now called in _build_filter_queryset with default ordering
        mock_queryset.order_by.assert_called_once_with("-balance")

    @patch("src.infrastructure.wallets.repositories.WalletModel.objects")
    def test_get_filter_queryset_returns_queryset(self, mock_objects):
        """Test that _build_filter_queryset returns a QuerySet."""
        # Arrange
        mock_queryset = Mock(spec=QuerySet)
        mock_objects.all.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset

        # Act
        result = self.repository._build_filter_queryset()

        # Assert
        assert result == mock_queryset
        mock_objects.all.assert_called_once()
        # Should call order_by with default ordering
        mock_queryset.order_by.assert_called_once_with("-balance")

    @patch("src.infrastructure.wallets.repositories.WalletModel.objects")
    def test_filter_wallets_empty_wallet_ids_list(self, mock_objects):
        """Test filtering with empty wallet_ids list returns all wallets (no filter applied)."""
        # Arrange
        mock_queryset = Mock(spec=QuerySet)
        mock_objects.all.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = [
            Mock(
                id=self.wallet_id_1,
                label="Test Wallet 1",
                balance=Decimal("1000"),
                is_active=True,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
            Mock(
                id=self.wallet_id_2,
                label="Test Wallet 2",
                balance=Decimal("2000"),
                is_active=False,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
            Mock(
                id=self.wallet_id_3,
                label="Test Wallet 3",
                balance=Decimal("3000"),
                is_active=True,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
        ]

        # Act
        result = self.repository.filter_wallets(wallet_ids=[])

        # Assert
        assert len(result) == 3
        mock_objects.all.assert_called_once()
        # Empty list is falsy, so no filter is applied
        mock_queryset.filter.assert_not_called()
        # order_by is now called in _build_filter_queryset with default ordering
        mock_queryset.order_by.assert_called_once_with("-balance")

    @patch("src.infrastructure.wallets.repositories.WalletModel.objects")
    def test_filter_wallets_none_wallet_ids(self, mock_objects):
        """Test filtering with None wallet_ids."""
        # Arrange
        mock_queryset = Mock(spec=QuerySet)
        mock_objects.all.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = [
            Mock(
                id=self.wallet_id_1,
                label="Test Wallet 1",
                balance=Decimal("1000"),
                is_active=True,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
            Mock(
                id=self.wallet_id_2,
                label="Test Wallet 2",
                balance=Decimal("2000"),
                is_active=False,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
            Mock(
                id=self.wallet_id_3,
                label="Test Wallet 3",
                balance=Decimal("3000"),
                is_active=True,
                deactivated_at=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            ),
        ]

        # Act
        result = self.repository.filter_wallets(wallet_ids=None)

        # Assert
        assert len(result) == 3
        mock_queryset.filter.assert_not_called()
        # order_by is now called in _build_filter_queryset with default ordering
        mock_queryset.order_by.assert_called_once_with("-balance")
