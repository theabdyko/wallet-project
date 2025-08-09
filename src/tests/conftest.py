"""
Pytest configuration and common fixtures.

This module provides shared fixtures and test utilities for the entire test suite,
ensuring consistent test data and reducing duplication across test files.
"""
# Standard library imports
from decimal import Decimal
from uuid import uuid4

# Third-party imports
import pytest
from django.test import TestCase

# Local imports
from src.domain.shared.types import Money, TransactionId, TxId, WalletId
from src.domain.transactions.entities import Transaction
from src.domain.wallets.entities import Wallet
from src.infrastructure.transactions.models import Transaction as TransactionModel
from src.infrastructure.wallets.models import Wallet as WalletModel


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Ensure Django database is properly set up for tests."""
    with django_db_blocker.unblock():
        # This ensures the database is created and configured
        pass


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass


# =============================================================================
# Domain Entity Fixtures
# =============================================================================


@pytest.fixture
def sample_wallet_id():
    """Provide a sample wallet ID."""
    return WalletId(uuid4())


@pytest.fixture
def sample_transaction_id():
    """Provide a sample transaction ID."""
    return TransactionId(uuid4())


@pytest.fixture
def sample_txid():
    """Provide a sample transaction external ID."""
    return TxId(f"tx_{uuid4().hex[:16]}")


@pytest.fixture
def sample_money():
    """Provide a sample money amount."""
    return Money(Decimal("100.00"))


@pytest.fixture
def sample_wallet(sample_wallet_id, sample_money):
    """Provide a sample wallet entity."""
    return Wallet(id=sample_wallet_id, label="Test Wallet", balance=sample_money)


@pytest.fixture
def sample_transaction(sample_transaction_id, sample_wallet_id, sample_txid):
    """Provide a sample transaction entity."""
    return Transaction(
        id=sample_transaction_id,
        wallet_id=sample_wallet_id,
        txid=sample_txid,
        amount=Money(Decimal("50.00")),
    )


# =============================================================================
# Django Model Fixtures
# =============================================================================


@pytest.fixture
def sample_wallet_model(sample_wallet_id):
    """Provide a sample wallet Django model instance."""
    return WalletModel(
        id=sample_wallet_id.value,
        label="Test Wallet",
        balance=Decimal("100.00"),
        is_active=True,
    )


@pytest.fixture
def sample_transaction_model(sample_transaction_id, sample_wallet_id, sample_txid):
    """Provide a sample transaction Django model instance."""
    return TransactionModel(
        id=sample_transaction_id.value,
        wallet_id=sample_wallet_id.value,
        txid=sample_txid.value,
        amount=Decimal("50.00"),
        is_active=True,
    )


# =============================================================================
# Factory Fixtures
# =============================================================================


@pytest.fixture
def wallet_factory():
    """Factory for creating wallet entities with customizable attributes."""

    def _create_wallet(
        wallet_id: WalletId | None = None,
        label: str = "Test Wallet",
        balance: Money | None = None,
        is_active: bool = True,
    ) -> Wallet:
        if wallet_id is None:
            wallet_id = WalletId(uuid4())
        if balance is None:
            balance = Money(Decimal("100.00"))

        return Wallet(id=wallet_id, label=label, balance=balance, is_active=is_active)

    return _create_wallet


@pytest.fixture
def transaction_factory():
    """Factory for creating transaction entities with customizable attributes."""

    def _create_transaction(
        transaction_id: TransactionId | None = None,
        wallet_id: WalletId | None = None,
        txid: TxId | None = None,
        amount: Money | None = None,
        is_active: bool = True,
    ) -> Transaction:
        if transaction_id is None:
            transaction_id = TransactionId(uuid4())
        if wallet_id is None:
            wallet_id = WalletId(uuid4())
        if txid is None:
            txid = TxId(f"tx_{uuid4().hex[:16]}")
        if amount is None:
            amount = Money(Decimal("50.00"))

        return Transaction(
            id=transaction_id,
            wallet_id=wallet_id,
            txid=txid,
            amount=amount,
            is_active=is_active,
        )

    return _create_transaction


@pytest.fixture
def wallet_model_factory():
    """Factory for creating wallet Django models with customizable attributes."""

    def _create_wallet_model(
        wallet_id: WalletId | None = None,
        label: str = "Test Wallet",
        balance: Decimal | None = None,
        is_active: bool = True,
    ) -> WalletModel:
        if wallet_id is None:
            wallet_id = WalletId(uuid4())
        if balance is None:
            balance = Decimal("100.00")

        return WalletModel(
            id=wallet_id.value, label=label, balance=balance, is_active=is_active
        )

    return _create_wallet_model


@pytest.fixture
def transaction_model_factory():
    """Factory for creating transaction Django models with customizable attributes."""

    def _create_transaction_model(
        transaction_id: TransactionId | None = None,
        wallet_id: WalletId | None = None,
        txid: TxId | None = None,
        amount: Decimal | None = None,
        is_active: bool = True,
    ) -> TransactionModel:
        if transaction_id is None:
            transaction_id = TransactionId(uuid4())
        if wallet_id is None:
            wallet_id = WalletId(uuid4())
        if txid is None:
            txid = TxId(f"tx_{uuid4().hex[:16]}")
        if amount is None:
            amount = Decimal("50.00")

        return TransactionModel(
            id=transaction_id.value,
            wallet_id=wallet_id.value,
            txid=txid.value,
            amount=amount,
            is_active=is_active,
        )

    return _create_transaction_model


# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def sample_wallet_ids():
    """Provide a list of sample wallet IDs."""
    return [WalletId(uuid4()) for _ in range(3)]


@pytest.fixture
def sample_transaction_ids():
    """Provide a list of sample transaction IDs."""
    return [TransactionId(uuid4()) for _ in range(3)]


@pytest.fixture
def sample_txids():
    """Provide a list of sample transaction external IDs."""
    return [TxId(f"tx_{uuid4().hex[:16]}") for _ in range(3)]


@pytest.fixture
def sample_money_amounts():
    """Provide a list of sample money amounts."""
    return [
        Money(Decimal("100.00")),
        Money(Decimal("-50.00")),
        Money(Decimal("200.00")),
        Money(Decimal("0.00")),
    ]


# =============================================================================
# Base Test Classes
# =============================================================================


class DatabaseTestCase(TestCase):
    """Base test case for database-dependent tests."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.wallet_id = WalletId(uuid4())
        self.transaction_id = TransactionId(uuid4())
        self.txid = TxId(f"tx_{uuid4().hex[:16]}")

    def create_wallet_in_db(self, **kwargs):
        """Create a wallet in the database."""
        defaults = {
            "id": self.wallet_id.value,
            "label": "Test Wallet",
            "balance": Decimal("100.00"),
            "is_active": True,
        }
        defaults.update(kwargs)
        return WalletModel.objects.create(**defaults)

    def create_transaction_in_db(self, wallet_id=None, **kwargs):
        """Create a transaction in the database."""
        if wallet_id is None:
            wallet = self.create_wallet_in_db()
            wallet_id = wallet.id

        defaults = {
            "id": self.transaction_id.value,
            "wallet_id": wallet_id,
            "txid": self.txid.value,
            "amount": Decimal("50.00"),
            "is_active": True,
        }
        defaults.update(kwargs)
        return TransactionModel.objects.create(**defaults)
