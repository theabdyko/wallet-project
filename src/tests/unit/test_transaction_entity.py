"""
Unit tests for Transaction domain entity.
"""
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.shared.exceptions import TransactionAlreadyDeactivatedException
from src.domain.shared.types import Money, TransactionId, TxId
from src.domain.transactions.entities import Transaction


class TestTransactionEntity:
    """Test cases for Transaction domain entity."""

    def test_transaction_creation_with_valid_data(
        self, sample_transaction_id, sample_wallet_id, sample_txid
    ):
        """Test transaction creation with valid data."""
        amount = Money(Decimal("100.00"))

        transaction = Transaction(
            id=sample_transaction_id,
            wallet_id=sample_wallet_id,
            txid=sample_txid,
            amount=amount,
        )

        assert transaction.id == sample_transaction_id
        assert transaction.wallet_id == sample_wallet_id
        assert transaction.txid == sample_txid
        assert transaction.amount == amount
        assert transaction.is_active is True
        assert transaction.deactivated_at is None
        assert transaction.created_at is not None
        assert transaction.updated_at is not None

    def test_transaction_creation_with_negative_amount(
        self, sample_transaction_id, sample_wallet_id, sample_txid
    ):
        """Test transaction creation with negative amount."""
        amount = Money(Decimal("-50.00"))

        transaction = Transaction(
            id=sample_transaction_id,
            wallet_id=sample_wallet_id,
            txid=sample_txid,
            amount=amount,
        )

        assert transaction.amount == amount
        assert transaction.is_debit() is True
        assert transaction.is_credit() is False

    def test_transaction_creation_with_zero_amount(
        self, sample_transaction_id, sample_wallet_id, sample_txid
    ):
        """Test transaction creation with zero amount."""
        amount = Money(Decimal("0.00"))

        transaction = Transaction(
            id=sample_transaction_id,
            wallet_id=sample_wallet_id,
            txid=sample_txid,
            amount=amount,
        )

        assert transaction.amount == amount
        assert transaction.is_debit() is False
        assert transaction.is_credit() is False

    def test_transaction_deactivation_success(
        self, sample_transaction_id, sample_wallet_id, sample_txid
    ):
        """Test transaction deactivation successfully."""
        transaction = Transaction(
            id=sample_transaction_id,
            wallet_id=sample_wallet_id,
            txid=sample_txid,
            amount=Money(Decimal("100.00")),
        )

        assert transaction.is_active is True
        assert transaction.deactivated_at is None

        transaction.deactivate()

        assert transaction.is_active is False
        assert transaction.deactivated_at is not None
        assert isinstance(transaction.deactivated_at, datetime)

    def test_transaction_deactivation_already_deactivated_raises_error(
        self, sample_transaction_id, sample_wallet_id, sample_txid
    ):
        """Test transaction deactivation when already deactivated raises error."""
        transaction = Transaction(
            id=sample_transaction_id,
            wallet_id=sample_wallet_id,
            txid=sample_txid,
            amount=Money(Decimal("100.00")),
        )

        transaction.deactivate()

        with pytest.raises(
            TransactionAlreadyDeactivatedException,
            match="Transaction is already deactivated",
        ):
            transaction.deactivate()

    def test_transaction_credit_debit_detection(
        self, sample_transaction_id, sample_wallet_id, sample_txid
    ):
        """Test transaction credit/debit detection."""
        # Credit transaction
        credit_transaction = Transaction(
            id=sample_transaction_id,
            wallet_id=sample_wallet_id,
            txid=sample_txid,
            amount=Money(Decimal("100.00")),
        )
        assert credit_transaction.is_credit() is True
        assert credit_transaction.is_debit() is False

        # Debit transaction
        debit_transaction = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=sample_wallet_id,
            txid=TxId(f"tx_{uuid4().hex[:16]}"),
            amount=Money(Decimal("-50.00")),
        )
        assert debit_transaction.is_debit() is True
        assert debit_transaction.is_credit() is False

    def test_transaction_equality(
        self, sample_transaction_id, sample_wallet_id, sample_txid
    ):
        """Test transaction equality."""
        transaction1 = Transaction(
            id=sample_transaction_id,
            wallet_id=sample_wallet_id,
            txid=sample_txid,
            amount=Money(Decimal("100.00")),
        )

        transaction2 = Transaction(
            id=sample_transaction_id,
            wallet_id=sample_wallet_id,
            txid=sample_txid,
            amount=Money(Decimal("100.00")),
        )

        transaction3 = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=sample_wallet_id,
            txid=sample_txid,
            amount=Money(Decimal("100.00")),
        )

        assert transaction1 == transaction2
        assert transaction1 != transaction3
        assert transaction1 != "not a transaction"

    def test_transaction_hash(
        self, sample_transaction_id, sample_wallet_id, sample_txid
    ):
        """Test transaction hash."""
        transaction1 = Transaction(
            id=sample_transaction_id,
            wallet_id=sample_wallet_id,
            txid=sample_txid,
            amount=Money(Decimal("100.00")),
        )

        transaction2 = Transaction(
            id=sample_transaction_id,
            wallet_id=sample_wallet_id,
            txid=sample_txid,
            amount=Money(Decimal("100.00")),
        )

        assert hash(transaction1) == hash(transaction2)

    def test_transaction_string_representation(
        self, sample_transaction_id, sample_wallet_id, sample_txid
    ):
        """Test transaction string representation."""
        transaction = Transaction(
            id=sample_transaction_id,
            wallet_id=sample_wallet_id,
            txid=sample_txid,
            amount=Money(Decimal("100.00")),
        )

        str_transaction = str(transaction)
        assert str(sample_transaction_id) in str_transaction
        assert str(sample_wallet_id) in str_transaction
        assert str(sample_txid) in str_transaction
        assert str(transaction.amount) in str_transaction
        assert "active=True" in str_transaction
