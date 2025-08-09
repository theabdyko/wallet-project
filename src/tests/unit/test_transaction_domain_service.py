"""
Unit tests for transaction domain service.

These tests verify the transaction domain service functionality,
including auto-generation of unique transaction IDs.
"""
# Standard library imports

# Third-party imports
from unittest.mock import Mock, patch

import pytest

from src.domain.shared.types import TxId
from src.domain.transactions.entities import Transaction
from src.domain.transactions.repositories import TransactionRepository

# Local imports
from src.domain.transactions.services import TransactionDomainService


class TestTransactionDomainService:
    """Test TransactionDomainService functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.mock_repository = Mock(spec=TransactionRepository)
        self.service = TransactionDomainService(self.mock_repository)

    def test_create_transaction_auto_generates_txid(
        self, sample_wallet_id, sample_money
    ):
        """Test that create_transaction auto-generates a unique txid."""
        # Arrange
        # Mock the _generate_unique_txid method to return a predictable value
        with patch.object(self.service, "_generate_unique_txid") as mock_generate:
            mock_generate.return_value = TxId("tx_123456789")

            # Act
            result = self.service.create_transaction(
                wallet_id=sample_wallet_id, amount=sample_money
            )

            # Assert
            # Verify the transaction entity was created with correct attributes
            assert isinstance(result, Transaction)
            assert result.txid == TxId("tx_123456789")
            assert result.wallet_id == sample_wallet_id
            assert result.amount == sample_money
            assert result.is_active is True

            # Verify the txid generator was called
            mock_generate.assert_called_once()

            # Verify NO repository save was called (domain service only creates in memory)
            self.mock_repository.save.assert_not_called()

    def test_generate_unique_txid_creates_unique_ids(self):
        """Test that _generate_unique_txid creates unique transaction IDs."""
        # Arrange
        self.mock_repository.exists_by_txid.return_value = False

        # Act
        txid1 = self.service._generate_unique_txid()
        txid2 = self.service._generate_unique_txid()

        # Assert
        assert txid1 != txid2
        assert isinstance(txid1, str)
        assert isinstance(txid2, str)
        assert str(txid1).startswith("tx_")
        assert str(txid2).startswith("tx_")

    def test_generate_unique_txid_handles_collisions(self):
        """Test that _generate_unique_txid handles txid collisions."""
        # Arrange
        # First call returns True (collision), second call returns False (unique)
        self.mock_repository.exists_by_txid.side_effect = [True, False]

        # Act
        txid = self.service._generate_unique_txid()

        # Assert
        assert isinstance(txid, str)
        assert str(txid).startswith("tx_")
        # Should have called exists_by_txid twice (once for collision, once for success)
        assert self.mock_repository.exists_by_txid.call_count == 2

    def test_generate_unique_txid_fallback_to_uuid(self):
        """Test that _generate_unique_txid falls back to UUID when max attempts reached."""
        # Arrange
        # Always return True to simulate persistent collisions
        self.mock_repository.exists_by_txid.return_value = True

        # Act
        txid = self.service._generate_unique_txid()

        # Assert
        assert isinstance(txid, str)
        assert str(txid).startswith("tx_")
        # Should have called exists_by_txid max_attempts times
        assert self.mock_repository.exists_by_txid.call_count == 11

    def test_create_transaction_creates_entity_in_memory(
        self, sample_wallet_id, sample_money
    ):
        """Test that create_transaction creates transaction entity in memory without persistence."""
        # Arrange
        # Mock the _generate_unique_txid method
        with patch.object(self.service, "_generate_unique_txid") as mock_generate:
            mock_generate.return_value = TxId("tx_123456789")

            # Act
            result = self.service.create_transaction(
                wallet_id=sample_wallet_id, amount=sample_money
            )

            # Assert
            # Verify the transaction entity was created correctly
            assert isinstance(result, Transaction)
            assert result.wallet_id == sample_wallet_id
            assert result.amount == sample_money
            assert result.txid == TxId("tx_123456789")
            assert result.is_active is True

            # Verify NO repository save was called (domain service only creates in memory)
            self.mock_repository.save.assert_not_called()

    def test_create_transaction_generates_different_txids_for_different_calls(
        self, sample_wallet_id, sample_money
    ):
        """Test that multiple calls to create_transaction generate different txids."""
        # Arrange
        # Mock the _generate_unique_txid method to return different values
        with patch.object(self.service, "_generate_unique_txid") as mock_generate:
            mock_generate.side_effect = [TxId("tx_123456789"), TxId("tx_987654321")]

            # Act
            result1 = self.service.create_transaction(
                wallet_id=sample_wallet_id, amount=sample_money
            )
            result2 = self.service.create_transaction(
                wallet_id=sample_wallet_id, amount=sample_money
            )

            # Assert
            # Verify different txids were generated
            assert result1.txid != result2.txid
            assert result1.txid == TxId("tx_123456789")
            assert result2.txid == TxId("tx_987654321")

            # Verify both transactions are valid entities
            assert isinstance(result1, Transaction)
            assert isinstance(result2, Transaction)
            assert result1.wallet_id == sample_wallet_id
            assert result2.wallet_id == sample_wallet_id
            assert result1.amount == sample_money
            assert result2.amount == sample_money

            # Verify NO repository save was called (domain service only creates in memory)
            self.mock_repository.save.assert_not_called()

    def test_create_transaction_returns_new_transaction_entity(
        self, sample_wallet_id, sample_money
    ):
        """Test that create_transaction returns a new Transaction entity instance."""
        # Arrange
        with patch.object(self.service, "_generate_unique_txid") as mock_generate:
            mock_generate.return_value = TxId("tx_test_123")

            # Act
            result = self.service.create_transaction(
                wallet_id=sample_wallet_id, amount=sample_money
            )

            # Assert
            # Verify it's a new Transaction entity
            assert isinstance(result, Transaction)
            assert result.id is not None
            assert result.wallet_id == sample_wallet_id
            assert result.amount == sample_money
            assert result.txid == TxId("tx_test_123")
            assert result.is_active is True
            assert result.created_at is not None
            assert result.updated_at is not None

            # Verify NO repository save was called (domain service only creates in memory)
            self.mock_repository.save.assert_not_called()
