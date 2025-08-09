"""
Functional tests for Transaction repository with database interaction.

These tests verify the actual database operations and persistence
of transaction entities through the repository layer.
"""
# Standard library imports
from decimal import Decimal
from uuid import uuid4

# Third-party imports
import pytest

# Local imports
from src.domain.shared.types import Money, TransactionId, TxId, WalletId
from src.domain.transactions.entities import Transaction
from src.infrastructure.transactions.models import Transaction as TransactionModel
from src.infrastructure.transactions.repositories import DjangoTransactionRepository
from src.infrastructure.wallets.models import Wallet as WalletModel


@pytest.mark.django_db
class TestDjangoTransactionRepository:
    """Functional tests for Django transaction repository."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.repository = DjangoTransactionRepository()
        self.wallet_id = WalletId(uuid4())
        self.transaction_id = TransactionId(uuid4())
        self.txid = TxId(f"tx_{uuid4().hex[:16]}")

        # Create a test wallet
        self.wallet = WalletModel.objects.create(
            id=self.wallet_id,
            label="Test Wallet",
            balance=Decimal("100.00"),
            is_active=True,
        )

    def test_save_transaction_successfully(self):
        """Test saving transaction to database successfully."""
        # Arrange
        transaction = Transaction(
            id=self.transaction_id,
            wallet_id=self.wallet_id,
            txid=self.txid,
            amount=Money(Decimal("100.00")),
        )

        # Act
        self.repository.save(transaction)

        # Assert
        saved_transaction = TransactionModel.objects.get(id=transaction.id)
        assert saved_transaction.wallet_id == transaction.wallet_id
        assert saved_transaction.txid == transaction.txid
        assert saved_transaction.amount == transaction.amount
        assert saved_transaction.is_active == transaction.is_active

        # Verify domain entity conversion
        domain_transaction = self.repository.get_by_id(transaction.id)
        assert domain_transaction is not None
        assert domain_transaction.id == transaction.id
        assert domain_transaction.wallet_id == transaction.wallet_id
        assert domain_transaction.txid == transaction.txid
        assert domain_transaction.amount == transaction.amount
        assert domain_transaction.is_active == transaction.is_active

    def test_save_transaction_updates_existing(self):
        """Test saving transaction updates existing record."""
        # Arrange
        transaction = Transaction(
            id=self.transaction_id,
            wallet_id=self.wallet_id,
            txid=self.txid,
            amount=Money(Decimal("100.00")),
        )

        # Save initial transaction
        self.repository.save(transaction)

        # Update transaction
        updated_transaction = Transaction(
            id=self.transaction_id,
            wallet_id=self.wallet_id,
            txid=self.txid,
            amount=Money(Decimal("200.00")),
        )

        # Act
        self.repository.save(updated_transaction)

        # Assert
        saved_transaction = TransactionModel.objects.get(id=transaction.id)
        assert saved_transaction.amount == Decimal("200.00")

    def test_get_by_id_successfully(self):
        """Test getting transaction by ID successfully."""
        # Arrange
        transaction = Transaction(
            id=self.transaction_id,
            wallet_id=self.wallet_id,
            txid=self.txid,
            amount=Money(Decimal("100.00")),
        )
        self.repository.save(transaction)

        # Act
        result = self.repository.get_by_id(self.transaction_id)

        # Assert
        assert result is not None
        assert result.id == self.transaction_id
        assert result.wallet_id == self.wallet_id
        assert result.txid == self.txid
        assert result.amount == Money(Decimal("100.00"))
        assert result.is_active is True

    def test_get_by_id_not_found_returns_none(self):
        """Test getting transaction by ID when not found returns None."""
        # Act
        result = self.repository.get_by_id(self.transaction_id)

        # Assert
        assert result is None

    def test_get_by_txid_successfully(self):
        """Test getting transaction by txid successfully."""
        # Arrange
        transaction = Transaction(
            id=self.transaction_id,
            wallet_id=self.wallet_id,
            txid=self.txid,
            amount=Money(Decimal("100.00")),
        )
        self.repository.save(transaction)

        # Act
        result = self.repository.get_active_by_txid(self.txid)

        # Assert
        assert result is not None
        assert result.id == self.transaction_id
        assert result.wallet_id == self.wallet_id
        assert result.txid == self.txid
        assert result.amount == Money(Decimal("100.00"))
        assert result.is_active is True

    def test_get_by_txid_not_found_returns_none(self):
        """Test getting transaction by txid when not found returns None."""
        # Act
        result = self.repository.get_active_by_txid(self.txid)

        # Assert
        assert result is None

    def test_get_by_wallet_id_successfully(self):
        """Test getting transactions by wallet ID successfully."""
        # Arrange
        transaction1 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=self.wallet_id,
            txid=TxId(f"tx_{uuid4().hex[:16]}"),
            amount=Money(Decimal("100.00")),
        )
        transaction2 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=self.wallet_id,
            txid=TxId(f"tx_{uuid4().hex[:16]}"),
            amount=Money(Decimal("200.00")),
        )

        self.repository.save(transaction1)
        self.repository.save(transaction2)

        # Act
        result = self.repository.get_active_by_wallet_id(self.wallet_id)

        # Assert
        assert len(result) == 2
        result_amounts = [t.amount for t in result]
        assert Money(Decimal("100.00")) in result_amounts
        assert Money(Decimal("200.00")) in result_amounts

    def test_get_by_wallet_ids_successfully(self):
        """Test getting transactions by multiple wallet IDs successfully."""
        # Arrange
        wallet2_id = WalletId(uuid4())
        WalletModel.objects.create(
            id=wallet2_id,
            label="Test Wallet 2",
            balance=Decimal("200.00"),
            is_active=True,
        )

        transaction1 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=self.wallet_id,
            txid=TxId(f"tx_{uuid4().hex[:16]}"),
            amount=Money(Decimal("100.00")),
        )
        transaction2 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=wallet2_id,
            txid=TxId(f"tx_{uuid4().hex[:16]}"),
            amount=Money(Decimal("200.00")),
        )

        self.repository.save(transaction1)
        self.repository.save(transaction2)

        # Act
        result = self.repository.get_by_wallet_ids([self.wallet_id, wallet2_id])

        # Assert
        assert len(result) == 2
        result_amounts = [t.amount for t in result]
        assert Money(Decimal("100.00")) in result_amounts
        assert Money(Decimal("200.00")) in result_amounts

    def test_get_by_wallet_ids_empty_list(self):
        """Test getting transactions by empty wallet IDs list returns empty list."""
        # Act
        result = self.repository.get_by_wallet_ids([])

        # Assert
        assert result == []

    def test_list_transactions_with_filters(self):
        """Test listing transactions with filters."""
        # Arrange
        wallet2_id = WalletId(uuid4())
        WalletModel.objects.create(
            id=wallet2_id,
            label="Test Wallet 2",
            balance=Decimal("200.00"),
            is_active=True,
        )

        transaction1 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=self.wallet_id,
            txid=TxId(f"tx_{uuid4().hex[:16]}"),
            amount=Money(Decimal("100.00")),
        )
        transaction2 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=wallet2_id,
            txid=TxId(f"tx_{uuid4().hex[:16]}"),
            amount=Money(Decimal("200.00")),
        )

        self.repository.save(transaction1)
        self.repository.save(transaction2)

        # Act
        result = self.repository.filter_transactions(
            is_active=True, wallet_ids=[self.wallet_id]
        )

        # Assert
        assert len(result) == 1
        assert result[0].wallet_id == self.wallet_id
        assert result[0].amount == Money(Decimal("100.00"))

    def test_list_transactions_without_filters(self):
        """Test listing transactions without filters."""
        # Arrange
        transaction1 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=self.wallet_id,
            txid=TxId(f"tx_{uuid4().hex[:16]}"),
            amount=Money(Decimal("100.00")),
        )
        transaction2 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=self.wallet_id,
            txid=TxId(f"tx_{uuid4().hex[:16]}"),
            amount=Money(Decimal("200.00")),
        )

        self.repository.save(transaction1)
        self.repository.save(transaction2)

        # Act
        result = self.repository.filter_transactions()

        # Assert
        assert len(result) == 2
        result_amounts = [t.amount for t in result]
        assert Money(Decimal("100.00")) in result_amounts
        assert Money(Decimal("200.00")) in result_amounts

    def test_list_transactions_with_only_is_active_filter(self):
        """Test listing transactions with only is_active filter."""
        # Arrange
        transaction1 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=self.wallet_id,
            txid=TxId(f"tx_{uuid4().hex[:16]}"),
            amount=Money(Decimal("100.00")),
        )
        transaction2 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=self.wallet_id,
            txid=TxId(f"tx_{uuid4().hex[:16]}"),
            amount=Money(Decimal("200.00")),
        )

        self.repository.save(transaction1)
        self.repository.save(transaction2)

        # Deactivate one transaction
        transaction2.deactivate()
        self.repository.save(transaction2)

        # Act
        result = self.repository.filter_transactions(is_active=True)

        # Assert
        assert len(result) == 1
        assert result[0].is_active is True
        assert result[0].amount == Money(Decimal("100.00"))

    def test_save_deactivated_transaction(self):
        """Test saving deactivated transaction."""
        # Arrange
        transaction = Transaction(
            id=self.transaction_id,
            wallet_id=self.wallet_id,
            txid=self.txid,
            amount=Money(Decimal("100.00")),
            is_active=False,
        )

        # Act
        self.repository.save(transaction)

        # Assert
        saved_transaction = TransactionModel.objects.get(id=transaction.id)
        assert saved_transaction.is_active is False
        assert saved_transaction.wallet_id == transaction.wallet_id
        assert saved_transaction.txid == transaction.txid
        assert saved_transaction.amount == transaction.amount

    def test_save_transaction_with_negative_amount(self):
        """Test saving transaction with negative amount."""
        # Arrange
        transaction = Transaction(
            id=self.transaction_id,
            wallet_id=self.wallet_id,
            txid=self.txid,
            amount=Money(Decimal("-100.00")),  # Negative amount
        )

        # Act
        self.repository.save(transaction)

        # Assert
        saved_transaction = TransactionModel.objects.get(id=transaction.id)
        assert saved_transaction.amount == Decimal("-100.00")
        assert saved_transaction.wallet_id == transaction.wallet_id
        assert saved_transaction.txid == transaction.txid

    def test_transaction_with_zero_amount(self):
        """Test saving transaction with zero amount."""
        # Arrange
        transaction = Transaction(
            id=self.transaction_id,
            wallet_id=self.wallet_id,
            txid=self.txid,
            amount=Money(Decimal("0.00")),  # Zero amount
        )

        # Act
        self.repository.save(transaction)

        # Assert
        saved_transaction = TransactionModel.objects.get(id=transaction.id)
        assert saved_transaction.amount == Decimal("0.00")
        assert saved_transaction.wallet_id == transaction.wallet_id
        assert saved_transaction.txid == transaction.txid
