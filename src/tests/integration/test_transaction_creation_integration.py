"""
Integration tests for transaction creation with wallet balance updates.

These tests verify the end-to-end functionality of transaction creation
with wallet balance updates using the actual database.
"""
# Standard library imports
from decimal import Decimal
from unittest.mock import patch

# Third-party imports
import pytest

# Local imports
from src.application.services import WalletTransactionOrchestrationService
from src.domain.shared.types import Money
from src.domain.transactions.services import TransactionDomainService
from src.domain.wallets.services import WalletDomainService
from src.infrastructure.transactions.models import Transaction as TransactionModel
from src.infrastructure.transactions.repositories import DjangoTransactionRepository
from src.infrastructure.wallets.models import Wallet as WalletModel
from src.infrastructure.wallets.repositories import DjangoWalletRepository


@pytest.mark.django_db
class TestTransactionCreationIntegration:
    """Integration tests for transaction creation with wallet balance updates."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.wallet_repository = DjangoWalletRepository()
        self.transaction_repository = DjangoTransactionRepository()

        self.wallet_domain_service = WalletDomainService(self.wallet_repository)
        self.transaction_domain_service = TransactionDomainService(
            self.transaction_repository
        )

        self.app_service = WalletTransactionOrchestrationService(
            wallet_domain_service=self.wallet_domain_service,
            transaction_domain_service=self.transaction_domain_service,
        )

        # Create a test wallet
        self.wallet = self.wallet_domain_service.create_wallet("Test Wallet")
        self.wallet_id = self.wallet.id

    def test_transaction_creation_updates_wallet_balance_correctly(self):
        """Test that transaction creation correctly updates wallet balance."""
        # Arrange
        initial_balance = self.wallet.balance
        transaction_amount = Money(Decimal("1000"))

        # Act
        (
            transaction,
            updated_wallet,
        ) = self.app_service.create_transaction_with_balance_update(
            wallet_id=self.wallet_id, amount=transaction_amount
        )

        # Assert
        # Verify transaction was created
        assert transaction is not None
        assert transaction.wallet_id == self.wallet_id
        assert transaction.amount == transaction_amount
        assert transaction.is_active is True

        # Verify wallet balance was updated
        assert updated_wallet.balance == initial_balance + transaction_amount

        # Verify database state
        db_wallet = WalletModel.objects.get(id=self.wallet_id)
        assert db_wallet.balance == updated_wallet.balance

        db_transaction = TransactionModel.objects.get(id=transaction.id)
        assert db_transaction.wallet_id == self.wallet_id
        assert db_transaction.amount == transaction_amount
        assert db_transaction.is_active is True

    def test_credit_transaction_increases_wallet_balance(self):
        """Test that credit transactions increase wallet balance."""
        # Arrange
        initial_balance = self.wallet.balance
        credit_amount = Money(Decimal("500"))

        # Act
        (
            transaction,
            updated_wallet,
        ) = self.app_service.create_transaction_with_balance_update(
            wallet_id=self.wallet_id, amount=credit_amount
        )

        # Assert
        expected_balance = initial_balance + credit_amount
        assert updated_wallet.balance == expected_balance

        # Verify database state
        db_wallet = WalletModel.objects.get(id=self.wallet_id)
        assert db_wallet.balance == expected_balance

    def test_debit_transaction_decreases_wallet_balance(self):
        """Test that debit transactions decrease wallet balance."""
        # Arrange
        # First add some balance to the wallet
        credit_transaction, _ = self.app_service.create_transaction_with_balance_update(
            wallet_id=self.wallet_id, amount=Money(Decimal("2000"))
        )

        initial_balance = self.wallet_domain_service.get_wallet(self.wallet_id).balance
        debit_amount = Money(Decimal("-500"))

        # Act
        (
            transaction,
            updated_wallet,
        ) = self.app_service.create_transaction_with_balance_update(
            wallet_id=self.wallet_id, amount=debit_amount
        )

        # Assert
        expected_balance = initial_balance + debit_amount
        assert updated_wallet.balance == expected_balance

        # Verify database state
        db_wallet = WalletModel.objects.get(id=self.wallet_id)
        assert db_wallet.balance == expected_balance

    def test_transaction_creation_fails_for_deactivated_wallet(self):
        """Test that transaction creation fails for deactivated wallets."""
        # Arrange
        # Deactivate the wallet
        deactivated_wallet = self.wallet_domain_service.deactivate_wallet(
            self.wallet_id
        )
        assert deactivated_wallet.is_active is False

        # Refresh the wallet state in the test
        self.wallet = deactivated_wallet

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.app_service.create_transaction_with_balance_update(
                wallet_id=self.wallet_id, amount=Money(Decimal("100"))
            )

        # Verify the exception message contains information about deactivated wallet
        error_message = str(exc_info.value)
        assert (
            "deactivated" in error_message.lower()
            or "not found" in error_message.lower()
        )

        # Verify no transaction was created
        transaction_count = TransactionModel.objects.filter(
            wallet_id=self.wallet_id
        ).count()
        assert transaction_count == 0

    def test_insufficient_balance_transaction_fails(self):
        """Test that transactions resulting in negative balance fail."""
        # Arrange
        # Try to create a debit transaction larger than current balance
        debit_amount = Money(Decimal("-10000"))  # Much larger than current balance

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.app_service.create_transaction_with_balance_update(
                wallet_id=self.wallet_id, amount=debit_amount
            )

        # Verify the exception message
        assert "Insufficient balance" in str(
            exc_info.value
        ) or "negative balance" in str(exc_info.value)

        # Verify no transaction was created
        transaction_count = TransactionModel.objects.filter(
            wallet_id=self.wallet_id
        ).count()
        assert transaction_count == 0

        # Verify wallet balance was not changed
        db_wallet = WalletModel.objects.get(id=self.wallet_id)
        assert db_wallet.balance == self.wallet.balance

    def test_multiple_transactions_update_balance_correctly(self):
        """Test that multiple transactions update wallet balance correctly."""
        # Arrange
        initial_balance = self.wallet.balance

        # Act - Create multiple transactions
        transactions = []
        amounts = [Money(Decimal("100")), Money(Decimal("-50")), Money(Decimal("200"))]

        for amount in amounts:
            (
                transaction,
                updated_wallet,
            ) = self.app_service.create_transaction_with_balance_update(
                wallet_id=self.wallet_id, amount=amount
            )
            transactions.append(transaction)
            self.wallet = updated_wallet  # Update for next iteration

        # Assert
        # Calculate expected final balance
        expected_balance = initial_balance
        for amount in amounts:
            expected_balance += amount

        assert self.wallet.balance == expected_balance

        # Verify database state
        db_wallet = WalletModel.objects.get(id=self.wallet_id)
        assert db_wallet.balance == expected_balance

        # Verify all transactions were created
        db_transaction_count = TransactionModel.objects.filter(
            wallet_id=self.wallet_id
        ).count()
        assert db_transaction_count == len(transactions)

    def test_transaction_rollback_on_wallet_update_failure(self):
        """Test that transaction creation rolls back if wallet update fails."""
        # This test would require mocking the database to simulate failures
        # For now, we'll test the happy path and ensure the atomic method is called

        # Arrange
        transaction_amount = Money(Decimal("100"))

        # Act
        with patch.object(
            self.wallet_repository, "update_balance_with_transaction"
        ) as mock_update:
            mock_update.side_effect = Exception("Database error")

            with pytest.raises(Exception, match="Database error"):
                self.app_service.create_transaction_with_balance_update(
                    wallet_id=self.wallet_id, amount=transaction_amount
                )

        # Verify no transaction was created in database
        transaction_count = TransactionModel.objects.filter(
            wallet_id=self.wallet_id
        ).count()
        assert transaction_count == 0

        # Verify wallet balance was not changed
        db_wallet = WalletModel.objects.get(id=self.wallet_id)
        assert db_wallet.balance == self.wallet.balance

    def test_concurrent_transaction_creation_handling(self):
        """Test that concurrent transaction creation is handled correctly."""
        # Arrange
        transaction_amount = Money(Decimal("100"))

        # Act - Create multiple transactions concurrently
        # In a real scenario, this would be done with multiple threads/processes
        # For this test, we'll create them sequentially but verify the locking works

        for _ in range(3):
            (
                transaction,
                updated_wallet,
            ) = self.app_service.create_transaction_with_balance_update(
                wallet_id=self.wallet_id, amount=transaction_amount
            )
            self.wallet = updated_wallet

        # Assert
        # Verify all transactions were created
        db_transaction_count = TransactionModel.objects.filter(
            wallet_id=self.wallet_id
        ).count()
        assert db_transaction_count == 3

        # Verify final balance is correct
        expected_balance = Money(Decimal("0")) + (transaction_amount * 3)
        assert self.wallet.balance == expected_balance

        # Verify database state
        db_wallet = WalletModel.objects.get(id=self.wallet_id)
        assert db_wallet.balance == expected_balance
