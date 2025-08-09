"""
Unit tests for Wallet domain entity.

These tests verify the pure domain logic of the Wallet entity,
including validation rules and business invariants.
"""
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.shared.exceptions import (
    WalletAlreadyDeactivatedException,
)
from src.domain.shared.types import Money, TransactionId, TxId, WalletId
from src.domain.transactions.entities import Transaction
from src.domain.wallets.entities import Wallet


class TestWalletEntity:
    """Test cases for Wallet domain entity."""

    def test_wallet_creation_with_valid_data(self, sample_wallet_id, sample_money):
        """Test wallet creation with valid data."""
        label = "Test Wallet"

        wallet = Wallet(id=sample_wallet_id, label=label, balance=sample_money)

        assert wallet.id == sample_wallet_id
        assert wallet.label == label
        assert wallet.balance == sample_money
        assert wallet.is_active is True
        assert wallet.deactivated_at is None
        assert wallet.created_at is not None
        assert wallet.updated_at is not None

    def test_wallet_creation_with_zero_balance(self, sample_wallet_id):
        """Test wallet creation with zero balance."""
        wallet = Wallet(
            id=sample_wallet_id, label="Test Wallet", balance=Money(Decimal("0.00"))
        )

        assert wallet.balance == Money(Decimal("0.00"))
        assert wallet.is_active is True

    def test_wallet_update_label_successfully(self, sample_wallet):
        """Test updating wallet label successfully."""
        new_label = "New Label"
        old_updated_at = sample_wallet.updated_at

        sample_wallet.update_label(new_label)

        assert sample_wallet.label == new_label
        assert sample_wallet.updated_at > old_updated_at

    def test_wallet_update_label_with_empty_string_raises_error(self, sample_wallet):
        """Test updating wallet label with empty string raises error."""
        with pytest.raises(ValueError, match="Label cannot be empty"):
            sample_wallet.update_label("")

        with pytest.raises(ValueError, match="Label cannot be empty"):
            sample_wallet.update_label("   ")

    def test_wallet_update_label_with_whitespace_only_raises_error(self, sample_wallet):
        """Test updating wallet label with whitespace only raises error."""
        with pytest.raises(ValueError, match="Label cannot be empty"):
            sample_wallet.update_label("   \n\t   ")

    def test_wallet_add_transaction_successfully(
        self, sample_wallet, sample_transaction
    ):
        """Test adding transaction to wallet successfully."""
        initial_balance = sample_wallet.balance
        old_updated_at = sample_wallet.updated_at
        initial_transaction_count = len(sample_wallet.transactions)

        sample_wallet.add_transaction(sample_transaction)

        # Balance should remain unchanged (no longer calculated in domain layer)
        assert sample_wallet.balance == initial_balance

        # Transaction should be added to the list
        assert len(sample_wallet.transactions) == initial_transaction_count + 1
        assert sample_wallet.transactions[-1] == sample_transaction

        # Updated timestamp should be updated
        assert sample_wallet.updated_at > old_updated_at

    def test_wallet_add_transaction_to_deactivated_wallet_raises_error(
        self, sample_wallet, sample_transaction
    ):
        """Test adding transaction to deactivated wallet raises error."""
        # Deactivate the wallet first
        sample_wallet.deactivate()
        assert sample_wallet.is_active is False

        # Act & Assert
        with pytest.raises(
            WalletAlreadyDeactivatedException,
            match="Cannot add transaction to deactivated wallet",
        ):
            sample_wallet.add_transaction(sample_transaction)

        # Verify wallet state hasn't changed
        assert len(sample_wallet.transactions) == 0

    def test_wallet_deactivate_successfully(self, sample_wallet):
        """Test deactivating wallet successfully."""
        assert sample_wallet.is_active is True
        assert sample_wallet.deactivated_at is None

        sample_wallet.deactivate()

        assert sample_wallet.is_active is False
        assert sample_wallet.deactivated_at is not None
        assert isinstance(sample_wallet.deactivated_at, datetime)

    def test_wallet_deactivate_already_deactivated_raises_error(self, sample_wallet):
        """Test deactivating already deactivated wallet raises error."""
        # Deactivate once
        sample_wallet.deactivate()

        # Try to deactivate again
        with pytest.raises(
            WalletAlreadyDeactivatedException, match="Wallet is already deactivated"
        ):
            sample_wallet.deactivate()

    def test_wallet_get_active_transactions(self, sample_wallet):
        """Test getting active transactions from wallet."""
        # Add some transactions
        transaction1 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=sample_wallet.id,
            txid=TxId("tx_1"),
            amount=Money(Decimal("50.00")),
        )
        transaction2 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=sample_wallet.id,
            txid=TxId("tx_2"),
            amount=Money(Decimal("25.00")),
        )

        sample_wallet.add_transaction(transaction1)
        sample_wallet.add_transaction(transaction2)

        # Get active transactions
        active_transactions = sample_wallet.get_active_transactions()

        assert len(active_transactions) == 2
        assert transaction1 in active_transactions
        assert transaction2 in active_transactions

        # Deactivate one transaction
        transaction1.deactivate()

        # Get active transactions again
        active_transactions = sample_wallet.get_active_transactions()

        assert len(active_transactions) == 1
        assert transaction2 in active_transactions
        assert transaction1 not in active_transactions

    def test_wallet_calculate_balance_from_transactions(self, sample_wallet):
        """Test calculating balance from transactions."""
        # Add some transactions
        transaction1 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=sample_wallet.id,
            txid=TxId("tx_1"),
            amount=Money(Decimal("50.00")),
        )
        transaction2 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=sample_wallet.id,
            txid=TxId("tx_2"),
            amount=Money(Decimal("-25.00")),  # Debit transaction
        )

        sample_wallet.add_transaction(transaction1)
        sample_wallet.add_transaction(transaction2)

        # Calculate balance from transactions
        calculated_balance = sample_wallet.calculate_balance_from_transactions()

        # Should be sum of transaction amounts: 50.00 + (-25.00) = 25.00
        assert calculated_balance == Money(Decimal("25.00"))

        # Deactivate one transaction
        transaction1.deactivate()

        # Calculate balance again (only active transactions)
        calculated_balance = sample_wallet.calculate_balance_from_transactions()

        # Should only include active transaction: -25.00
        assert calculated_balance == Money(Decimal("-25.00"))

    def test_wallet_equality(self, sample_wallet_id, sample_money):
        """Test wallet equality comparison."""
        wallet1 = Wallet(
            id=sample_wallet_id, label="Test Wallet 1", balance=sample_money
        )
        wallet2 = Wallet(
            id=sample_wallet_id,  # Same ID
            label="Test Wallet 2",  # Different label
            balance=Money(Decimal("200.00")),  # Different balance
        )
        wallet3 = Wallet(
            id=WalletId(uuid4()),  # Different ID
            label="Test Wallet 1",
            balance=sample_money,
        )

        # Same ID should be equal regardless of other attributes
        assert wallet1 == wallet2

        # Different ID should not be equal
        assert wallet1 != wallet3

        # Should not be equal to non-wallet objects
        assert wallet1 != "not a wallet"
        assert wallet1 != 123

    def test_wallet_hash(self, sample_wallet_id, sample_money):
        """Test wallet hash functionality."""
        wallet1 = Wallet(
            id=sample_wallet_id, label="Test Wallet 1", balance=sample_money
        )
        wallet2 = Wallet(
            id=sample_wallet_id,  # Same ID
            label="Test Wallet 2",  # Different label
            balance=Money(Decimal("200.00")),  # Different balance
        )

        # Same ID should have same hash
        assert hash(wallet1) == hash(wallet2)

        # Hash should be consistent
        assert hash(wallet1) == hash(wallet1)

    def test_wallet_repr(self, sample_wallet):
        """Test wallet string representation."""
        repr_string = repr(sample_wallet)

        assert "Wallet" in repr_string
        assert str(sample_wallet.id) in repr_string
        assert sample_wallet.label in repr_string
        assert str(sample_wallet.balance) in repr_string
        assert str(sample_wallet.is_active) in repr_string

    def test_wallet_str(self, sample_wallet):
        """Test wallet string conversion."""
        str_string = str(sample_wallet)

        assert "Wallet" in str_string
        assert str(sample_wallet.id) in str_string
        assert sample_wallet.label in str_string
        assert str(sample_wallet.balance) in str_string
        assert str(sample_wallet.is_active) in str_string
