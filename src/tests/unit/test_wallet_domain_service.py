"""
Unit tests for wallet domain service.
"""
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest

from src.domain.shared.exceptions import WalletNotFoundException
from src.domain.shared.types import Money, WalletId
from src.domain.wallets.entities import Wallet
from src.domain.wallets.repositories import WalletRepository
from src.domain.wallets.services import WalletDomainService


class TestWalletDomainService:
    """Test wallet domain service."""

    @pytest.fixture
    def sample_wallet_id(self):
        """Sample wallet ID for testing."""
        return WalletId("123e4567-e89b-12d3-a456-426614174000")

    @pytest.fixture
    def sample_wallet(self, sample_wallet_id):
        """Sample wallet for testing."""
        return Wallet(
            id=sample_wallet_id,
            label="Test Wallet",
            balance=Money(Decimal("100.00")),
            is_active=True,
        )

    def test_get_wallet_by_id_success(self, sample_wallet):
        """Test getting wallet by ID successfully."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        mock_repository.get_active_by_id.return_value = sample_wallet
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act
        result = service.get_wallet(sample_wallet.id)

        # Assert
        assert result == sample_wallet
        mock_repository.get_active_by_id.assert_called_once_with(sample_wallet.id)

    def test_get_wallet_by_id_not_found_raises_error(self, sample_wallet_id):
        """Test getting wallet by ID when not found raises error."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        mock_repository.get_active_by_id.return_value = None
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act & Assert
        with pytest.raises(WalletNotFoundException):
            service.get_wallet(sample_wallet_id)

        mock_repository.get_active_by_id.assert_called_once_with(sample_wallet_id)

    def test_get_wallets_by_ids_success(self, sample_wallet):
        """Test getting wallets by IDs successfully."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        mock_repository.get_by_ids.return_value = [sample_wallet]
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act
        result = service.get_wallets_by_ids([sample_wallet.id])

        # Assert
        assert result == [sample_wallet]
        mock_repository.get_by_ids.assert_called_once_with([sample_wallet.id])

    def test_get_wallets_by_ids_empty_list(self):
        """Test getting wallets by IDs with empty list."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        mock_repository.get_by_ids.return_value = []
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act
        result = service.get_wallets_by_ids([])

        # Assert
        assert result == []
        mock_repository.get_by_ids.assert_called_once_with([])

    def test_get_all_active_wallets_success(self, sample_wallet):
        """Test getting all active wallets successfully."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        mock_repository.get_all_active.return_value = [sample_wallet]
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act
        result = service.get_all_active_wallets()

        # Assert
        assert result == [sample_wallet]
        mock_repository.get_all_active.assert_called_once()

    def test_list_wallets_with_filters_success(self, sample_wallet):
        """Test listing wallets with filters successfully."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        mock_repository.get_by_ids.return_value = [sample_wallet]
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act
        result = service.get_wallets_by_ids([sample_wallet.id])

        # Assert
        assert result == [sample_wallet]
        mock_repository.get_by_ids.assert_called_once_with([sample_wallet.id])

    def test_list_wallets_without_filters_success(self, sample_wallet):
        """Test listing wallets without filters successfully."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        mock_repository.get_all_active.return_value = [sample_wallet]
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act
        result = service.get_all_active_wallets()

        # Assert
        assert result == [sample_wallet]
        mock_repository.get_all_active.assert_called_once()

    def test_update_wallet_label_success(self, sample_wallet):
        """Test updating wallet label successfully."""
        # Arrange
        new_label = "Updated Label"
        mock_repository = Mock(spec=WalletRepository)
        mock_repository.get_active_by_id.return_value = sample_wallet
        mock_repository.save.return_value = sample_wallet
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act
        result = service.update_wallet_label(sample_wallet.id, new_label)

        # Assert
        assert result == sample_wallet
        assert sample_wallet.label == new_label
        mock_repository.get_active_by_id.assert_called_once_with(sample_wallet.id)
        mock_repository.save.assert_called_once_with(sample_wallet)

    def test_update_wallet_label_wallet_not_found_raises_error(self, sample_wallet_id):
        """Test updating wallet label when wallet not found raises error."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        mock_repository.get_active_by_id.return_value = None
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act & Assert
        with pytest.raises(WalletNotFoundException):
            service.update_wallet_label(sample_wallet_id, "New Label")

        mock_repository.get_active_by_id.assert_called_once_with(sample_wallet_id)
        mock_repository.save.assert_not_called()

    def test_deactivate_wallet_success(self, sample_wallet):
        """Test deactivating wallet successfully."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        mock_repository.get_active_by_id.return_value = sample_wallet
        mock_repository.save.return_value = sample_wallet
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act
        result = service.deactivate_wallet(sample_wallet.id)

        # Assert
        assert result == sample_wallet
        assert sample_wallet.is_active is False
        assert sample_wallet.deactivated_at is not None
        mock_repository.get_active_by_id.assert_called_once_with(sample_wallet.id)
        mock_repository.save.assert_called_once_with(sample_wallet)

    def test_deactivate_wallet_already_deactivated(self, sample_wallet):
        """Test deactivating already deactivated wallet raises error."""
        # Arrange
        # Create a deactivated wallet
        Wallet(
            id=sample_wallet.id,
            label=sample_wallet.label,
            balance=sample_wallet.balance,
            is_active=False,
            deactivated_at=datetime.utcnow(),
        )

        mock_repository = Mock(spec=WalletRepository)
        mock_repository.get_active_by_id.return_value = (
            None  # get_active_by_id returns None for deactivated wallet
        )
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act & Assert
        with pytest.raises(WalletNotFoundException):
            service.deactivate_wallet(sample_wallet.id)

        mock_repository.get_active_by_id.assert_called_once_with(sample_wallet.id)
        mock_repository.save.assert_not_called()

    def test_deactivate_wallet_not_found_raises_error(self, sample_wallet_id):
        """Test deactivating wallet when not found raises error."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        mock_repository.get_active_by_id.return_value = None
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act & Assert
        with pytest.raises(WalletNotFoundException):
            service.deactivate_wallet(sample_wallet_id)

        mock_repository.get_active_by_id.assert_called_once_with(sample_wallet_id)
        mock_repository.save.assert_not_called()

    def test_filter_wallets_no_filters(self, sample_wallet):
        """Test filtering wallets with no filters returns all wallets."""
        # Arrange
        mock_repository = Mock()
        mock_repository.filter_wallets = Mock(return_value=[sample_wallet])
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act
        result = service.filter_wallets()

        # Assert
        assert result == [sample_wallet]
        # Verify the method was called with correct parameters
        mock_repository.filter_wallets.assert_called_once()
        call_args = mock_repository.filter_wallets.call_args
        assert call_args[0] == (None, None)  # (is_active, wallet_ids)

    def test_filter_wallets_only_is_active_true(self, sample_wallet):
        """Test filtering wallets with only is_active=True filter."""
        # Arrange
        mock_repository = Mock()
        mock_repository.filter_wallets = Mock(return_value=[sample_wallet])
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act
        result = service.filter_wallets(is_active=True)

        # Assert
        assert result == [sample_wallet]
        # Verify the method was called with correct parameters
        mock_repository.filter_wallets.assert_called_once()
        call_args = mock_repository.filter_wallets.call_args
        assert call_args[0] == (True, None)  # (is_active, wallet_ids)

    def test_filter_wallets_only_is_active_false(self, sample_wallet):
        """Test filtering wallets with only is_active=False filter."""
        # Arrange
        mock_repository = Mock()
        mock_repository.filter_wallets = Mock(return_value=[sample_wallet])
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act
        result = service.filter_wallets(is_active=False)

        # Assert
        assert result == [sample_wallet]
        # Verify the method was called with correct parameters
        mock_repository.filter_wallets.assert_called_once()
        call_args = mock_repository.filter_wallets.call_args
        assert call_args[0] == (False, None)  # (is_active, wallet_ids)

    def test_filter_wallets_only_wallet_ids(self, sample_wallet):
        """Test filtering wallets with only wallet_ids filter."""
        # Arrange
        mock_repository = Mock()
        mock_repository.filter_wallets = Mock(return_value=[sample_wallet])
        service = WalletDomainService(wallet_repository=mock_repository)

        wallet_ids = [sample_wallet.id]

        # Act
        result = service.filter_wallets(wallet_ids=wallet_ids)

        # Assert
        assert result == [sample_wallet]
        # Verify the method was called with correct parameters
        mock_repository.filter_wallets.assert_called_once()
        call_args = mock_repository.filter_wallets.call_args
        assert call_args[0] == (None, wallet_ids)  # (is_active, wallet_ids)

    def test_filter_wallets_both_filters_together(self, sample_wallet):
        """Test filtering wallets with both is_active and wallet_ids filters."""
        # Arrange
        mock_repository = Mock()
        mock_repository.filter_wallets = Mock(return_value=[sample_wallet])
        service = WalletDomainService(wallet_repository=mock_repository)

        wallet_ids = [sample_wallet.id]

        # Act
        result = service.filter_wallets(is_active=True, wallet_ids=wallet_ids)

        # Assert
        assert result == [sample_wallet]
        # Verify the method was called with correct parameters
        mock_repository.filter_wallets.assert_called_once()
        call_args = mock_repository.filter_wallets.call_args
        assert call_args[0] == (True, wallet_ids)  # (is_active, wallet_ids)

    def test_create_wallet_success(self):
        """Test creating a wallet successfully."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        mock_wallet = Mock(spec=Wallet)
        mock_repository.save.return_value = mock_wallet
        service = WalletDomainService(wallet_repository=mock_repository)

        label = "Test Wallet"

        # Act
        result = service.create_wallet(label)

        # Assert
        assert result == mock_wallet
        mock_repository.save.assert_called_once()

        # Verify the saved wallet has correct attributes
        saved_wallet = mock_repository.save.call_args[0][0]
        assert saved_wallet.label == label
        assert saved_wallet.balance == Money(0)
        assert saved_wallet.is_active is True

    def test_create_wallet_empty_label_raises_error(self):
        """Test creating a wallet with empty label raises error."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        service = WalletDomainService(wallet_repository=mock_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Wallet label cannot be empty"):
            service.create_wallet("")

        with pytest.raises(ValueError, match="Wallet label cannot be empty"):
            service.create_wallet("   ")

        with pytest.raises(ValueError, match="Wallet label cannot be empty"):
            service.create_wallet(None)

        # Verify repository was not called
        mock_repository.save.assert_not_called()

    def test_create_wallet_whitespace_label_trimmed(self):
        """Test creating a wallet with whitespace label gets trimmed."""
        # Arrange
        mock_repository = Mock(spec=WalletRepository)
        mock_wallet = Mock(spec=Wallet)
        mock_repository.save.return_value = mock_wallet
        service = WalletDomainService(wallet_repository=mock_repository)

        label = "  Test Wallet  "

        # Act
        result = service.create_wallet(label)

        # Assert
        assert result == mock_wallet
        mock_repository.save.assert_called_once()

        # Verify the saved wallet has trimmed label
        saved_wallet = mock_repository.save.call_args[0][0]
        assert saved_wallet.label == "Test Wallet"
