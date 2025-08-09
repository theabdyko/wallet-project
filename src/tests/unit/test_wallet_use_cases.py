"""
Unit tests for wallet use cases.
"""
from unittest.mock import Mock
from uuid import UUID

import pytest

from src.application.wallets.queries import (
    ListWalletsQuery,
    ListWalletsUseCase,
    ListWalletsWithPaginationQuery,
    ListWalletsWithPaginationUseCase,
)
from src.domain.shared.types import WalletId
from src.domain.wallets.entities import Wallet
from src.domain.wallets.repositories import WalletRepository


class TestListWalletsUseCase:
    """Test cases for ListWalletsUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_application_service = Mock()
        # Ensure the list_wallets method is properly mocked
        self.mock_application_service.list_wallets = Mock()
        self.use_case = ListWalletsUseCase(self.mock_application_service)

        # Create test wallet IDs
        self.wallet_id_1 = WalletId(UUID("123e4567-e89b-12d3-a456-426614174000"))
        self.wallet_id_2 = WalletId(UUID("987fcdeb-51a2-43d1-b567-987654321000"))

        # Create test wallets
        self.wallet_1 = Mock(spec=Wallet)
        self.wallet_1.id = self.wallet_id_1
        self.wallet_2 = Mock(spec=Wallet)
        self.wallet_2.id = self.wallet_id_2

    def test_execute_no_filters(self):
        """Test executing use case with no filters."""
        # Arrange
        query = ListWalletsQuery()
        self.mock_application_service.list_wallets.return_value = [
            self.wallet_1,
            self.wallet_2,
        ]

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == [self.wallet_1, self.wallet_2]
        self.mock_application_service.list_wallets.assert_called_once_with(
            is_active=None, wallet_ids=None
        )

    def test_execute_only_is_active_filter_true(self):
        """Test executing use case with only is_active=True filter."""
        # Arrange
        query = ListWalletsQuery(is_active_str="true")
        self.mock_application_service.list_wallets.return_value = [self.wallet_1]

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == [self.wallet_1]
        self.mock_application_service.list_wallets.assert_called_once_with(
            is_active=True, wallet_ids=None
        )

    def test_execute_only_is_active_filter_false(self):
        """Test executing use case with only is_active=False filter."""
        # Arrange
        query = ListWalletsQuery(is_active_str="false")
        self.mock_application_service.list_wallets.return_value = [self.wallet_2]

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == [self.wallet_2]
        self.mock_application_service.list_wallets.assert_called_once_with(
            is_active=False, wallet_ids=None
        )

    def test_execute_only_wallet_ids_filter(self):
        """Test executing use case with only wallet_ids filter."""
        # Arrange
        query = ListWalletsQuery(
            wallet_ids_str=["123e4567-e89b-12d3-a456-426614174000"]
        )
        self.mock_application_service.list_wallets.return_value = [self.wallet_1]

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == [self.wallet_1]
        self.mock_application_service.list_wallets.assert_called_once_with(
            is_active=None, wallet_ids=[self.wallet_id_1]
        )

    def test_execute_both_filters_together(self):
        """Test executing use case with both filters together."""
        # Arrange
        query = ListWalletsQuery(
            is_active_str="true",
            wallet_ids_str=["123e4567-e89b-12d3-a456-426614174000"],
        )
        self.mock_application_service.list_wallets.return_value = [self.wallet_1]

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == [self.wallet_1]
        self.mock_application_service.list_wallets.assert_called_once_with(
            is_active=True, wallet_ids=[self.wallet_id_1]
        )

    def test_execute_invalid_is_active_raises_error(self):
        """Test executing use case with invalid is_active value raises error."""
        # Arrange
        query = ListWalletsQuery(is_active_str="invalid")

        # Act & Assert
        with pytest.raises(
            ValueError, match="is_active filter must be 'true' or 'false'"
        ):
            self.use_case.execute(query)

    def test_execute_invalid_wallet_id_format_raises_error(self):
        """Test executing use case with invalid wallet ID format raises error."""
        # Arrange
        query = ListWalletsQuery(wallet_ids_str=["invalid-uuid"])

        # Act & Assert
        with pytest.raises(
            ValueError, match="Invalid wallet ID format in wallet_ids filter"
        ):
            self.use_case.execute(query)


class TestListWalletsWithPaginationUseCase:
    """Test cases for ListWalletsWithPaginationUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_repository = Mock(spec=WalletRepository)
        self.use_case = ListWalletsWithPaginationUseCase(self.mock_repository)

        # Create test wallet IDs
        self.wallet_id_1 = WalletId(UUID("123e4567-e89b-12d3-a456-426614174000"))
        self.wallet_id_2 = WalletId(UUID("987fcdeb-51a2-43d1-b567-987654321000"))

        # Create mock queryset
        self.mock_queryset = Mock()

    def test_execute_no_filters(self):
        """Test executing use case with no filters."""
        # Arrange
        query = ListWalletsWithPaginationQuery()
        self.mock_repository.get_filtered_queryset.return_value = self.mock_queryset

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == self.mock_queryset
        self.mock_repository.get_filtered_queryset.assert_called_once_with(
            is_active=None, wallet_ids=None
        )

    def test_execute_only_is_active_filter_true(self):
        """Test executing use case with only is_active=True filter."""
        # Arrange
        query = ListWalletsWithPaginationQuery(is_active_str="true")
        self.mock_repository.get_filtered_queryset.return_value = self.mock_queryset

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == self.mock_queryset
        self.mock_repository.get_filtered_queryset.assert_called_once_with(
            is_active=True, wallet_ids=None
        )

    def test_execute_only_is_active_filter_false(self):
        """Test executing use case with only is_active=False filter."""
        # Arrange
        query = ListWalletsWithPaginationQuery(is_active_str="false")
        self.mock_repository.get_filtered_queryset.return_value = self.mock_queryset

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == self.mock_queryset
        self.mock_repository.get_filtered_queryset.assert_called_once_with(
            is_active=False, wallet_ids=None
        )

    def test_execute_only_wallet_ids_filter(self):
        """Test executing use case with only wallet_ids filter."""
        # Arrange
        query = ListWalletsWithPaginationQuery(
            wallet_ids_str=["123e4567-e89b-12d3-a456-426614174000"]
        )
        self.mock_repository.get_filtered_queryset.return_value = self.mock_queryset

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == self.mock_queryset
        self.mock_repository.get_filtered_queryset.assert_called_once_with(
            is_active=None, wallet_ids=[self.wallet_id_1]
        )

    def test_execute_both_filters_together(self):
        """Test executing use case with both filters together."""
        # Arrange
        query = ListWalletsWithPaginationQuery(
            is_active_str="true",
            wallet_ids_str=["123e4567-e89b-12d3-a456-426614174000"],
        )
        self.mock_repository.get_filtered_queryset.return_value = self.mock_queryset

        # Act
        result = self.use_case.execute(query)

        # Assert
        assert result == self.mock_queryset
        self.mock_repository.get_filtered_queryset.assert_called_once_with(
            is_active=True, wallet_ids=[self.wallet_id_1]
        )

    def test_execute_invalid_is_active_raises_error(self):
        """Test executing use case with invalid is_active value raises error."""
        # Arrange
        query = ListWalletsWithPaginationQuery(is_active_str="invalid")

        # Act & Assert
        with pytest.raises(
            ValueError, match="is_active filter must be 'true' or 'false'"
        ):
            self.use_case.execute(query)

    def test_execute_invalid_wallet_id_format_raises_error(self):
        """Test executing use case with invalid wallet ID format raises error."""
        # Arrange
        query = ListWalletsWithPaginationQuery(wallet_ids_str=["invalid-uuid"])

        # Act & Assert
        with pytest.raises(
            ValueError, match="Invalid wallet ID format in wallet_ids filter"
        ):
            self.use_case.execute(query)
