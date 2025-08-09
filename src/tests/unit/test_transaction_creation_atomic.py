"""
Unit tests for atomic transaction creation with wallet balance updates.

These tests verify that transaction creation and wallet balance updates
happen atomically to ensure data consistency.
"""
# Standard library imports
from decimal import Decimal
from unittest.mock import Mock, patch

# Third-party imports
import pytest

# Local imports
from src.application.services import WalletTransactionOrchestrationService
from src.domain.shared.types import Money
from src.domain.transactions.repositories import TransactionRepository
from src.domain.transactions.services import TransactionDomainService
from src.domain.wallets.repositories import WalletRepository
from src.domain.wallets.services import WalletDomainService


class TestAtomicTransactionCreation:
    """Test atomic transaction creation with wallet balance updates."""

    @pytest.fixture(autouse=True)
    def setup(self, wallet_factory, transaction_factory):
        """Set up test data."""
        self.mock_wallet_repository = Mock(spec=WalletRepository)
        self.mock_transaction_repository = Mock(spec=TransactionRepository)

        self.wallet_domain_service = WalletDomainService(self.mock_wallet_repository)
        self.transaction_domain_service = TransactionDomainService(
            self.mock_transaction_repository
        )

        self.app_service = WalletTransactionOrchestrationService(
            wallet_domain_service=self.wallet_domain_service,
            transaction_domain_service=self.transaction_domain_service,
        )

        # Store factories for use in tests
        self.wallet_factory = wallet_factory
        self.transaction_factory = transaction_factory

    def test_create_transaction_with_balance_update_success(
        self, sample_wallet_id, sample_money
    ):
        """Test successful transaction creation with wallet balance update."""
        # Arrange
        wallet = self.wallet_factory(wallet_id=sample_wallet_id, balance=sample_money)
        transaction = self.transaction_factory(amount=sample_money)

        self.mock_wallet_repository.get_active_by_id.return_value = wallet
        self.mock_wallet_repository.update_balance_with_transaction.return_value = (
            wallet
        )

        # Mock the transaction domain service to return our test transaction
        with patch.object(
            self.transaction_domain_service, "create_transaction"
        ) as mock_create:
            mock_create.return_value = transaction

            # Act
            (
                result_transaction,
                result_wallet,
            ) = self.app_service.create_transaction_with_balance_update(
                wallet_id=sample_wallet_id, amount=sample_money
            )

            # Assert
            assert result_transaction == transaction
            assert result_wallet == wallet

            # Verify wallet was retrieved
            self.mock_wallet_repository.get_active_by_id.assert_called_once_with(
                sample_wallet_id
            )

            # Verify transaction was created
            mock_create.assert_called_once_with(
                wallet_id=sample_wallet_id, amount=sample_money
            )

            # Verify atomic update was called
            self.mock_wallet_repository.update_balance_with_transaction.assert_called_once()

            # Verify the correct parameters were passed to update_balance_with_transaction
            call_args = (
                self.mock_wallet_repository.update_balance_with_transaction.call_args[0]
            )
            updated_wallet = call_args[0]
            transaction = call_args[1]

            # The wallet should have the transaction added to its list
            assert transaction in updated_wallet.transactions

    def test_create_transaction_with_balance_update_deactivated_wallet(
        self, sample_wallet_id, sample_money
    ):
        """Test transaction creation fails for deactivated wallet."""
        # Arrange
        deactivated_wallet = self.wallet_factory(
            wallet_id=sample_wallet_id, balance=sample_money, is_active=False
        )
        self.mock_wallet_repository.get_active_by_id.return_value = deactivated_wallet

        # Act & Assert
        with pytest.raises(
            ValueError, match="Cannot create transaction for deactivated wallet"
        ):
            self.app_service.create_transaction_with_balance_update(
                wallet_id=sample_wallet_id, amount=sample_money
            )

        # Verify no further calls were made
        self.mock_wallet_repository.update_balance_with_transaction.assert_not_called()

    def test_create_transaction_with_balance_update_insufficient_balance(
        self, sample_wallet_id
    ):
        """Test transaction creation fails when it would result in negative balance."""
        # Arrange
        wallet = self.wallet_factory(
            wallet_id=sample_wallet_id, balance=Money(Decimal("5000"))
        )
        self.mock_wallet_repository.get_active_by_id.return_value = wallet

        # Mock the transaction domain service to return a transaction
        with patch.object(
            self.transaction_domain_service, "create_transaction"
        ) as mock_create:
            transaction = self.transaction_factory(amount=Money(Decimal("-10000")))
            mock_create.return_value = transaction

            # Mock the repository to raise an exception for negative balance
            self.mock_wallet_repository.update_balance_with_transaction.side_effect = ValueError(
                "Transaction would result in negative balance. Current: 5000, Transaction: -10000, New Balance: -5000"
            )

            # Try to create a transaction that would result in negative balance
            negative_amount = Money(Decimal("-10000"))  # Would result in -5000 balance

            # Act & Assert
            with pytest.raises(
                ValueError, match="Transaction would result in negative balance"
            ):
                self.app_service.create_transaction_with_balance_update(
                    wallet_id=sample_wallet_id, amount=negative_amount
                )

            # Verify atomic update was called (it gets called but raises an exception)
            self.mock_wallet_repository.update_balance_with_transaction.assert_called_once()

    def test_create_transaction_with_balance_update_zero_amount(self, sample_wallet_id):
        """Test transaction creation fails with zero amount."""
        # Arrange
        wallet = self.wallet_factory(
            wallet_id=sample_wallet_id, balance=Money(Decimal("1000"))
        )
        self.mock_wallet_repository.get_active_by_id.return_value = wallet

        # Mock the transaction domain service to return a transaction
        with patch.object(
            self.transaction_domain_service, "create_transaction"
        ) as mock_create:
            transaction = self.transaction_factory(amount=Money(Decimal("0")))
            mock_create.return_value = transaction

            # Mock the repository to raise an exception for zero amount
            self.mock_wallet_repository.update_balance_with_transaction.side_effect = (
                ValueError("Transaction amount cannot be zero")
            )

            zero_amount = Money(Decimal("0"))

            # Act & Assert
            with pytest.raises(ValueError, match="Transaction amount cannot be zero"):
                self.app_service.create_transaction_with_balance_update(
                    wallet_id=sample_wallet_id, amount=zero_amount
                )

            # Verify atomic update was called (it gets called but raises an exception)
            self.mock_wallet_repository.update_balance_with_transaction.assert_called_once()

    def test_create_transaction_with_balance_update_wallet_not_found(
        self, sample_wallet_id, sample_money
    ):
        """Test transaction creation fails when wallet is not found."""
        # Arrange
        self.mock_wallet_repository.get_active_by_id.return_value = None

        # Act & Assert
        with pytest.raises(Exception, match="Wallet with ID.*not found"):
            self.app_service.create_transaction_with_balance_update(
                wallet_id=sample_wallet_id, amount=sample_money
            )

        # Verify no further calls were made
        self.mock_wallet_repository.update_balance_with_transaction.assert_not_called()

    def test_create_transaction_with_balance_update_credit_transaction(
        self, sample_wallet_id
    ):
        """Test successful credit transaction creation."""
        # Arrange
        initial_balance = Money(Decimal("1000"))
        credit_amount = Money(Decimal("500"))

        wallet = self.wallet_factory(
            wallet_id=sample_wallet_id, balance=initial_balance
        )
        transaction = self.transaction_factory(amount=credit_amount)

        self.mock_wallet_repository.get_active_by_id.return_value = wallet
        self.mock_wallet_repository.update_balance_with_transaction.return_value = (
            wallet
        )

        with patch.object(
            self.transaction_domain_service, "create_transaction"
        ) as mock_create:
            mock_create.return_value = transaction

            # Act
            (
                result_transaction,
                result_wallet,
            ) = self.app_service.create_transaction_with_balance_update(
                wallet_id=sample_wallet_id, amount=credit_amount
            )

            # Assert
            assert result_transaction == transaction
            assert result_wallet == wallet

            # Verify atomic update was called
            self.mock_wallet_repository.update_balance_with_transaction.assert_called_once()

            # Verify the correct parameters were passed
            call_args = (
                self.mock_wallet_repository.update_balance_with_transaction.call_args[0]
            )
            updated_wallet = call_args[0]
            transaction = call_args[1]

            # The wallet should have the transaction added to its list
            assert transaction in updated_wallet.transactions

    def test_create_transaction_with_balance_update_debit_transaction(
        self, sample_wallet_id
    ):
        """Test successful debit transaction creation."""
        # Arrange
        initial_balance = Money(Decimal("1000"))
        debit_amount = Money(Decimal("-300"))

        wallet = self.wallet_factory(
            wallet_id=sample_wallet_id, balance=initial_balance
        )
        transaction = self.transaction_factory(amount=debit_amount)

        self.mock_wallet_repository.get_active_by_id.return_value = wallet
        self.mock_wallet_repository.update_balance_with_transaction.return_value = (
            wallet
        )

        with patch.object(
            self.transaction_domain_service, "create_transaction"
        ) as mock_create:
            mock_create.return_value = transaction

            # Act
            (
                result_transaction,
                result_wallet,
            ) = self.app_service.create_transaction_with_balance_update(
                wallet_id=sample_wallet_id, amount=debit_amount
            )

            # Assert
            assert result_transaction == transaction
            assert result_wallet == wallet

            # Verify atomic update was called
            self.mock_wallet_repository.update_balance_with_transaction.assert_called_once()

            # Verify the correct parameters were passed
            call_args = (
                self.mock_wallet_repository.update_balance_with_transaction.call_args[0]
            )
            updated_wallet = call_args[0]
            transaction = call_args[1]

            # The wallet should have the transaction added to its list
            assert transaction in updated_wallet.transactions

    def test_create_transaction_with_balance_update_exact_balance_debit(
        self, sample_wallet_id
    ):
        """Test debit transaction that results in exactly zero balance."""
        # Arrange
        initial_balance = Money(Decimal("500"))
        debit_amount = Money(Decimal("-500"))  # Will result in exactly 0 balance

        wallet = self.wallet_factory(
            wallet_id=sample_wallet_id, balance=initial_balance
        )
        transaction = self.transaction_factory(amount=debit_amount)

        self.mock_wallet_repository.get_active_by_id.return_value = wallet
        self.mock_wallet_repository.update_balance_with_transaction.return_value = (
            wallet
        )

        with patch.object(
            self.transaction_domain_service, "create_transaction"
        ) as mock_create:
            mock_create.return_value = transaction

            # Act
            (
                result_transaction,
                result_wallet,
            ) = self.app_service.create_transaction_with_balance_update(
                wallet_id=sample_wallet_id, amount=debit_amount
            )

            # Assert
            assert result_transaction == transaction
            assert result_wallet == wallet

            # Verify atomic update was called
            self.mock_wallet_repository.update_balance_with_transaction.assert_called_once()

            # Verify the correct parameters were passed
            call_args = (
                self.mock_wallet_repository.update_balance_with_transaction.call_args[0]
            )
            updated_wallet = call_args[0]
            transaction = call_args[1]

            # The wallet should have the transaction added to its list
            assert transaction in updated_wallet.transactions

    def test_create_transaction_with_balance_update_transaction_added_to_wallet(
        self, sample_wallet_id, sample_money
    ):
        """Test that transaction is added to wallet's transaction list."""
        # Arrange
        wallet = self.wallet_factory(wallet_id=sample_wallet_id, balance=sample_money)
        transaction = self.transaction_factory(amount=sample_money)

        self.mock_wallet_repository.get_active_by_id.return_value = wallet
        self.mock_wallet_repository.update_balance_with_transaction.return_value = (
            wallet
        )

        with patch.object(
            self.transaction_domain_service, "create_transaction"
        ) as mock_create:
            mock_create.return_value = transaction

            # Act
            (
                result_transaction,
                result_wallet,
            ) = self.app_service.create_transaction_with_balance_update(
                wallet_id=sample_wallet_id, amount=sample_money
            )

            # Assert
            assert result_transaction == transaction
            assert result_wallet == wallet

            # Verify atomic update was called
            self.mock_wallet_repository.update_balance_with_transaction.assert_called_once()

            # Verify the transaction was added to the wallet
            call_args = (
                self.mock_wallet_repository.update_balance_with_transaction.call_args[0]
            )
            updated_wallet = call_args[0]
            transaction = call_args[1]

            # The wallet should have the transaction added to its list
            assert transaction in updated_wallet.transactions
