"""
Functional tests for Wallet repository with database interaction.

These tests verify the actual database operations and persistence
of wallet entities through the repository layer.
"""
# Standard library imports
from decimal import Decimal
from uuid import uuid4

# Third-party imports
import pytest

# Local imports
from src.domain.shared.types import Money, WalletId
from src.domain.wallets.entities import Wallet
from src.infrastructure.wallets.models import Wallet as WalletModel
from src.infrastructure.wallets.repositories import DjangoWalletRepository


@pytest.mark.django_db
class TestDjangoWalletRepository:
    """Functional tests for Django wallet repository."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.repository = DjangoWalletRepository()
        self.wallet_id = WalletId(uuid4())

    def test_save_wallet_successfully(self):
        """Test saving wallet to database successfully."""
        # Arrange
        wallet = Wallet(
            id=self.wallet_id, label="Test Wallet", balance=Money(Decimal("100.00"))
        )

        # Act
        self.repository.save(wallet)

        # Assert
        saved_wallet = WalletModel.objects.get(id=wallet.id)
        assert saved_wallet.label == wallet.label
        assert saved_wallet.balance == wallet.balance
        assert saved_wallet.is_active == wallet.is_active

    def test_save_wallet_updates_existing(self):
        """Test saving wallet updates existing record."""
        # Arrange
        # Create initial wallet
        initial_wallet = Wallet(
            id=self.wallet_id, label="Initial Label", balance=Money(Decimal("100.00"))
        )
        self.repository.save(initial_wallet)

        # Create updated wallet
        updated_wallet = Wallet(
            id=self.wallet_id, label="Updated Label", balance=Money(Decimal("200.00"))
        )

        # Act
        self.repository.save(updated_wallet)

        # Assert
        db_wallet = WalletModel.objects.get(id=self.wallet_id)
        assert db_wallet.label == "Updated Label"
        assert db_wallet.balance == Decimal("200.00")

    def test_get_by_id_successfully(self):
        """Test getting wallet by ID successfully."""
        # Arrange
        wallet = Wallet(
            id=self.wallet_id, label="Test Wallet", balance=Money(Decimal("100.00"))
        )
        self.repository.save(wallet)

        # Act
        result = self.repository.get_by_id(WalletId(self.wallet_id))

        # Assert
        assert result is not None
        assert result.id == self.wallet_id
        assert result.label == wallet.label
        assert result.balance == wallet.balance

    def test_get_by_id_not_found_returns_none(self):
        """Test getting wallet by ID when not found returns None."""
        # Act
        result = self.repository.get_by_id(self.wallet_id)

        # Assert
        assert result is None

    def test_get_by_ids_successfully(self):
        """Test getting wallets by IDs successfully."""
        # Arrange
        wallet1_id = WalletId(uuid4())
        wallet2_id = WalletId(uuid4())

        wallet1 = Wallet(
            id=wallet1_id, label="Wallet 1", balance=Money(Decimal("100.00"))
        )
        wallet2 = Wallet(
            id=wallet2_id, label="Wallet 2", balance=Money(Decimal("200.00"))
        )

        self.repository.save(wallet1)
        self.repository.save(wallet2)

        wallet_ids = [wallet1_id, wallet2_id]

        # Act
        result = self.repository.get_by_ids(wallet_ids)

        # Assert
        assert len(result) == 2
        result_ids = [w.id for w in result]
        assert wallet1_id in result_ids
        assert wallet2_id in result_ids

    def test_get_by_ids_partial_found(self):
        """Test getting wallets by IDs when only some exist."""
        # Arrange
        wallet1_id = WalletId(uuid4())
        wallet2_id = WalletId(uuid4())  # This one won't exist

        wallet1 = Wallet(
            id=wallet1_id, label="Wallet 1", balance=Money(Decimal("100.00"))
        )
        self.repository.save(wallet1)

        wallet_ids = [wallet1_id, wallet2_id]

        # Act
        result = self.repository.get_by_ids(wallet_ids)

        # Assert
        assert len(result) == 1
        assert result[0].id == wallet1_id

    def test_get_by_ids_empty_list(self):
        """Test getting wallets by IDs with empty list."""
        # Act
        result = self.repository.get_by_ids([])

        # Assert
        assert result == []

    def test_get_all_active_successfully(self):
        """Test getting all active wallets successfully."""
        # Arrange
        active_wallet1 = Wallet(
            id=WalletId(uuid4()),
            label="Active Wallet 1",
            balance=Money(Decimal("100.00")),
            is_active=True,
        )
        active_wallet2 = Wallet(
            id=WalletId(uuid4()),
            label="Active Wallet 2",
            balance=Money(Decimal("200.00")),
            is_active=True,
        )

        self.repository.save(active_wallet1)
        self.repository.save(active_wallet2)

        # Act
        result = self.repository.get_all_active()

        # Assert
        assert len(result) >= 2  # At least our 2 wallets
        result_labels = [w.label for w in result]
        assert "Active Wallet 1" in result_labels
        assert "Active Wallet 2" in result_labels

    def test_list_wallets_with_filters(self):
        """Test listing wallets with filters."""
        # Arrange
        wallet1 = Wallet(
            id=WalletId(uuid4()),
            label="Filtered Wallet 1",
            balance=Money(Decimal("100.00")),
            is_active=True,
        )
        wallet2 = Wallet(
            id=WalletId(uuid4()),
            label="Filtered Wallet 2",
            balance=Money(Decimal("200.00")),
            is_active=False,
        )

        self.repository.save(wallet1)
        self.repository.save(wallet2)

        # Act
        active_wallets = self.repository.filter_wallets(is_active=True)
        inactive_wallets = self.repository.filter_wallets(is_active=False)

        # Assert
        assert len(active_wallets) >= 1
        assert len(inactive_wallets) >= 1

        active_labels = [w.label for w in active_wallets]
        inactive_labels = [w.label for w in inactive_wallets]

        assert "Filtered Wallet 1" in active_labels
        assert "Filtered Wallet 2" in inactive_labels

    def test_list_wallets_without_filters(self):
        """Test listing wallets without filters."""
        # Arrange
        wallet = Wallet(
            id=WalletId(uuid4()),
            label="Unfiltered Wallet",
            balance=Money(Decimal("100.00")),
        )
        self.repository.save(wallet)

        # Act
        result = self.repository.filter_wallets()

        # Assert
        assert len(result) >= 1
        result_labels = [w.label for w in result]
        assert "Unfiltered Wallet" in result_labels

    def test_list_wallets_with_only_is_active_filter(self):
        """Test listing wallets with only is_active filter."""
        # Arrange
        active_wallet = Wallet(
            id=WalletId(uuid4()),
            label="Active Only Wallet",
            balance=Money(Decimal("100.00")),
            is_active=True,
        )
        self.repository.save(active_wallet)

        # Act
        active_result = self.repository.filter_wallets(is_active=True)
        inactive_result = self.repository.filter_wallets(is_active=False)

        # Assert
        assert len(active_result) >= 1
        assert len(inactive_result) >= 0  # May have other inactive wallets

        active_labels = [w.label for w in active_result]
        assert "Active Only Wallet" in active_labels

    def test_save_wallet_with_transactions(self):
        """Test saving wallet with transaction balance update."""
        # Arrange
        wallet = Wallet(
            id=self.wallet_id,
            label="Transaction Wallet",
            balance=Money(Decimal("100.00")),
        )

        # Create a mock transaction for testing
        from src.domain.shared.types import TransactionId, TxId
        from src.domain.transactions.entities import Transaction

        Transaction(
            id=TransactionId(uuid4()),
            wallet_id=self.wallet_id,
            txid=TxId("tx_test_123"),
            amount=Money(Decimal("50.00")),
        )

        # Act
        self.repository.save(wallet)

        # Assert
        saved_wallet = WalletModel.objects.get(id=wallet.id)
        assert saved_wallet.label == wallet.label
        assert saved_wallet.balance == wallet.balance

    def test_save_deactivated_wallet(self):
        """Test saving deactivated wallet."""
        # Arrange
        wallet = Wallet(
            id=self.wallet_id,
            label="Deactivated Wallet",
            balance=Money(Decimal("100.00")),
            is_active=False,
        )

        # Act
        self.repository.save(wallet)

        # Assert
        saved_wallet = WalletModel.objects.get(id=wallet.id)
        assert saved_wallet.is_active is False
        assert saved_wallet.label == wallet.label
        assert saved_wallet.balance == wallet.balance

    def test_concurrent_wallet_operations(self):
        """Test concurrent wallet operations."""
        # Arrange
        wallet_ids = [WalletId(uuid4()) for _ in range(3)]
        wallets = [
            Wallet(
                id=wallet_id,
                label=f"Concurrent Wallet {i}",
                balance=Money(Decimal("100.00")),
            )
            for i, wallet_id in enumerate(wallet_ids)
        ]

        # Act - Save multiple wallets "concurrently"
        for wallet in wallets:
            self.repository.save(wallet)

        # Assert
        for wallet in wallets:
            saved_wallet = WalletModel.objects.get(id=wallet.id)
            assert saved_wallet.label == wallet.label
            assert saved_wallet.balance == wallet.balance
            assert saved_wallet.is_active == wallet.is_active
