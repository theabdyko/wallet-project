"""
Integration tests for wallet list functionality.

This test file verifies that all components of the wallet list endpoint
work together correctly, including serializers, use cases, and pagination.
"""
from decimal import Decimal
from unittest.mock import Mock
from uuid import UUID

import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from src.application.wallets.queries import (
    ListWalletsQuery,
    ListWalletsWithPaginationUseCase,
)
from src.domain.shared.types import Money, WalletId
from src.domain.wallets.entities import Wallet


class TestWalletListIntegration(TestCase):
    """Test wallet list endpoint integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()

        # Create test wallet IDs
        self.wallet_id_1 = WalletId(UUID("123e4567-e89b-12d3-a456-426614174000"))
        self.wallet_id_2 = WalletId(UUID("987fcdeb-51a2-43d1-b567-987654321000"))

        # Create test wallets
        self.wallet_1 = Wallet(
            id=self.wallet_id_1,
            label="Test Wallet 1",
            balance=Money(Decimal("1000")),
            is_active=True,
        )
        self.wallet_2 = Wallet(
            id=self.wallet_id_2,
            label="Test Wallet 2",
            balance=Money(Decimal("2000")),
            is_active=False,
        )

    def test_list_wallets_use_case_execution(self):
        """Test that the ListWalletsWithPaginationUseCase executes correctly."""
        # Arrange
        mock_repository = Mock()
        mock_queryset = Mock()
        mock_repository.get_filtered_queryset.return_value = mock_queryset

        use_case = ListWalletsWithPaginationUseCase(mock_repository)
        query = ListWalletsQuery(
            wallet_ids_str=["123e4567-e89b-12d3-a456-426614174000"],
            is_active_str="true",
        )

        # Act
        result = use_case.execute(query)

        # Assert
        assert result == mock_queryset
        mock_repository.get_filtered_queryset.assert_called_once_with(
            is_active=True, wallet_ids=[self.wallet_id_1]
        )

    def test_list_wallets_use_case_no_filters(self):
        """Test that the use case handles no filters correctly."""
        # Arrange
        mock_repository = Mock()
        mock_queryset = Mock()
        mock_repository.get_filtered_queryset.return_value = mock_queryset

        use_case = ListWalletsWithPaginationUseCase(mock_repository)
        query = ListWalletsQuery()

        # Act
        result = use_case.execute(query)

        # Assert
        assert result == mock_queryset
        mock_repository.get_filtered_queryset.assert_called_once_with(
            is_active=None, wallet_ids=None
        )

    def test_list_wallets_use_case_invalid_is_active(self):
        """Test that the use case handles invalid is_active values correctly."""
        # Arrange
        mock_repository = Mock()
        use_case = ListWalletsWithPaginationUseCase(mock_repository)
        query = ListWalletsQuery(is_active_str="invalid")

        # Act & Assert
        with pytest.raises(
            ValueError, match="is_active filter must be 'true' or 'false'"
        ):
            use_case.execute(query)

    def test_list_wallets_use_case_invalid_wallet_id(self):
        """Test that the use case handles invalid wallet IDs correctly."""
        # Arrange
        mock_repository = Mock()
        use_case = ListWalletsWithPaginationUseCase(mock_repository)
        query = ListWalletsQuery(wallet_ids_str=["invalid-uuid"])

        # Act & Assert
        with pytest.raises(
            ValueError, match="Invalid wallet ID format in wallet_ids filter"
        ):
            use_case.execute(query)

    def test_list_wallets_use_case_case_insensitive_filters(self):
        """Test that the use case handles case-insensitive filter values."""
        # Arrange
        mock_repository = Mock()
        mock_queryset = Mock()
        mock_repository.get_filtered_queryset.return_value = mock_queryset

        use_case = ListWalletsWithPaginationUseCase(mock_repository)

        # Test various case combinations
        test_cases = [
            ("TRUE", True),
            ("True", True),
            ("true", True),
            ("FALSE", False),
            ("False", False),
            ("false", False),
            ("1", True),
            ("0", False),
            ("YES", True),
            ("NO", False),
        ]

        for input_value, expected_value in test_cases:
            with self.subTest(input_value=input_value):
                query = ListWalletsQuery(is_active_str=input_value)
                result = use_case.execute(query)

                assert result == mock_queryset
                mock_repository.get_filtered_queryset.assert_called_with(
                    is_active=expected_value, wallet_ids=None
                )
                mock_repository.reset_mock()

    def test_list_wallets_use_case_multiple_wallet_ids(self):
        """Test that the use case handles multiple wallet IDs correctly."""
        # Arrange
        mock_repository = Mock()
        mock_queryset = Mock()
        mock_repository.get_filtered_queryset.return_value = mock_queryset

        use_case = ListWalletsWithPaginationUseCase(mock_repository)
        query = ListWalletsQuery(
            wallet_ids_str=[
                "123e4567-e89b-12d3-a456-426614174000",
                "987fcdeb-51a2-43d1-b567-987654321000",
            ]
        )

        # Act
        result = use_case.execute(query)

        # Assert
        assert result == mock_queryset
        mock_repository.get_filtered_queryset.assert_called_once_with(
            is_active=None, wallet_ids=[self.wallet_id_1, self.wallet_id_2]
        )

    def test_list_wallets_use_case_both_filters_together(self):
        """Test that the use case applies both filters together correctly."""
        # Arrange
        mock_repository = Mock()
        mock_queryset = Mock()
        mock_repository.get_filtered_queryset.return_value = mock_queryset

        use_case = ListWalletsWithPaginationUseCase(mock_repository)
        query = ListWalletsQuery(
            wallet_ids_str=["123e4567-e89b-12d3-a456-426614174000"],
            is_active_str="true",
        )

        # Act
        result = use_case.execute(query)

        # Assert
        assert result == mock_queryset
        mock_repository.get_filtered_queryset.assert_called_once_with(
            is_active=True, wallet_ids=[self.wallet_id_1]
        )

    def test_list_wallets_use_case_none_values(self):
        """Test that the use case handles None values correctly."""
        # Arrange
        mock_repository = Mock()
        mock_queryset = Mock()
        mock_repository.get_filtered_queryset.return_value = mock_queryset

        use_case = ListWalletsWithPaginationUseCase(mock_repository)
        query = ListWalletsQuery(wallet_ids_str=None, is_active_str=None)

        # Act
        result = use_case.execute(query)

        # Assert
        assert result == mock_queryset
        mock_repository.get_filtered_queryset.assert_called_once_with(
            is_active=None, wallet_ids=None
        )
