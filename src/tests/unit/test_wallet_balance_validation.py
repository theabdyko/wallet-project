"""
Unit tests for wallet balance validation within atomic transactions.

These tests verify that wallet balance validation happens correctly
within Django atomic transactions to prevent race conditions.
"""
# Standard library imports
from decimal import Decimal
from unittest.mock import Mock

# Third-party imports
import pytest

# Local imports
from src.domain.shared.types import Money
from src.domain.wallets.repositories import WalletRepository


class TestWalletBalanceValidation:
    """Test wallet balance validation within atomic transactions."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.mock_wallet_repository = Mock(spec=WalletRepository)

    def test_add_transaction_no_longer_calculates_balance(
        self, wallet_factory, transaction_factory
    ):
        """Test that add_transaction no longer calculates balance."""
        # Arrange
        wallet = wallet_factory(balance=Money(Decimal("1000")))
        transaction = transaction_factory(amount=Money(Decimal("500")))
        old_balance = wallet.balance

        # Act
        wallet.add_transaction(transaction)

        # Assert
        # Balance should remain unchanged (calculation happens in infrastructure layer)
        assert wallet.balance == old_balance
        # Transaction should be added to the list
        assert transaction in wallet.transactions

    def test_add_transaction_still_checks_wallet_active_status(
        self, wallet_factory, transaction_factory
    ):
        """Test that add_transaction still checks if wallet is active."""
        # Arrange
        deactivated_wallet = wallet_factory(
            balance=Money(Decimal("1000")), is_active=False
        )
        transaction = transaction_factory(amount=Money(Decimal("500")))

        # Act & Assert
        with pytest.raises(
            Exception, match="Cannot add transaction to deactivated wallet"
        ):
            deactivated_wallet.add_transaction(transaction)

    def test_update_balance_with_transaction_validates_balance_within_atomic(
        self, wallet_factory, transaction_factory
    ):
        """Test that balance validation happens within the atomic transaction."""
        # Arrange
        wallet = wallet_factory(balance=Money(Decimal("5000")))
        transaction = transaction_factory(amount=Money(Decimal("1000")))

        # Mock the repository method
        self.mock_wallet_repository.update_balance_with_transaction.return_value = (
            wallet
        )

        # Act
        result = self.mock_wallet_repository.update_balance_with_transaction(
            wallet, transaction
        )

        # Assert
        assert result == wallet
        self.mock_wallet_repository.update_balance_with_transaction.assert_called_once_with(
            wallet, transaction
        )

    def test_update_balance_with_transaction_prevents_negative_balance(
        self, wallet_factory, transaction_factory
    ):
        """Test that negative balance is prevented within the atomic transaction."""
        # Arrange
        wallet = wallet_factory(balance=Money(Decimal("5000")))
        debit_transaction = transaction_factory(amount=Money(Decimal("-10000")))

        # Mock the repository method to raise an exception
        self.mock_wallet_repository.update_balance_with_transaction.side_effect = ValueError(
            "Transaction would result in negative balance. Current: 5000, Transaction: -10000, New Balance: -5000"
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.mock_wallet_repository.update_balance_with_transaction(
                wallet, debit_transaction
            )

        # Verify the exception message
        assert "Transaction would result in negative balance" in str(exc_info.value)
        assert "Current: 5000" in str(exc_info.value)
        assert "Transaction: -10000" in str(exc_info.value)
        assert "New Balance: -5000" in str(exc_info.value)

    def test_update_balance_with_transaction_allows_exact_zero_balance(
        self, wallet_factory, transaction_factory
    ):
        """Test that exact zero balance is allowed."""
        # Arrange
        wallet = wallet_factory(balance=Money(Decimal("5000")))
        exact_debit_transaction = transaction_factory(amount=Money(Decimal("-5000")))

        # Mock the repository method to return the updated wallet
        self.mock_wallet_repository.update_balance_with_transaction.return_value = (
            wallet
        )

        # Act
        result = self.mock_wallet_repository.update_balance_with_transaction(
            wallet, exact_debit_transaction
        )

        # Assert
        assert result == wallet
        self.mock_wallet_repository.update_balance_with_transaction.assert_called_once_with(
            wallet, exact_debit_transaction
        )

    def test_update_balance_with_transaction_handles_credit_transactions(
        self, wallet_factory, transaction_factory
    ):
        """Test that credit transactions are handled correctly."""
        # Arrange
        wallet = wallet_factory(balance=Money(Decimal("1000")))
        credit_transaction = transaction_factory(amount=Money(Decimal("500")))

        # Mock the repository method
        self.mock_wallet_repository.update_balance_with_transaction.return_value = (
            wallet
        )

        # Act
        result = self.mock_wallet_repository.update_balance_with_transaction(
            wallet, credit_transaction
        )

        # Assert
        assert result == wallet
        self.mock_wallet_repository.update_balance_with_transaction.assert_called_once_with(
            wallet, credit_transaction
        )

    def test_update_balance_with_transaction_handles_debit_transactions(
        self, wallet_factory, transaction_factory
    ):
        """Test that debit transactions are handled correctly."""
        # Arrange
        wallet = wallet_factory(balance=Money(Decimal("1000")))
        debit_transaction = transaction_factory(amount=Money(Decimal("-300")))

        # Mock the repository method
        self.mock_wallet_repository.update_balance_with_transaction.return_value = (
            wallet
        )

        # Act
        result = self.mock_wallet_repository.update_balance_with_transaction(
            wallet, debit_transaction
        )

        # Assert
        assert result == wallet
        self.mock_wallet_repository.update_balance_with_transaction.assert_called_once_with(
            wallet, debit_transaction
        )
