"""
Transaction repository interface.
"""
from abc import ABC, abstractmethod

from src.domain.shared.types import TransactionId, TxId, WalletId
from src.domain.transactions.entities import Transaction


class TransactionRepository(ABC):
    """
    Abstract transaction repository interface.

    This follows the dependency inversion principle - the domain depends on abstractions,
    not concrete implementations.
    """

    @abstractmethod
    def get_by_id(self, transaction_id: TransactionId) -> Transaction | None:
        """
        Get transaction by ID.

        Args:
            transaction_id: Transaction ID to find

        Returns:
            Transaction entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_txid(self, txid: TxId) -> Transaction | None:
        """
        Get transaction by external transaction ID.

        Args:
            txid: External transaction ID to find

        Returns:
            Transaction entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_active_by_txid(self, txid: TxId) -> Transaction | None:
        """
        Get active transaction by external transaction ID.

        Args:
            txid: External transaction ID to find

        Returns:
            Active transaction entity if found, None otherwise
        """
        pass

    @abstractmethod
    def save(self, transaction: Transaction) -> Transaction:
        """
        Save transaction entity.

        Args:
            transaction: Transaction entity to save

        Returns:
            Saved transaction entity
        """
        pass

    @abstractmethod
    def get_by_wallet_id(self, wallet_id: WalletId) -> list[Transaction]:
        """
        Get all transactions for a wallet.

        Args:
            wallet_id: Wallet ID to find transactions for

        Returns:
            List of transaction entities
        """
        pass

    @abstractmethod
    def get_active_by_wallet_id(self, wallet_id: WalletId) -> list[Transaction]:
        """
        Get all active transactions for a wallet.

        Args:
            wallet_id: Wallet ID to find active transactions for

        Returns:
            List of active transaction entities
        """
        pass

    @abstractmethod
    def get_active_by_wallet_ids(self, wallet_ids: list[WalletId]) -> list[Transaction]:
        """
        Get all active transactions for multiple wallets.

        Args:
            wallet_ids: List of wallet IDs to find active transactions for

        Returns:
            List of active transaction entities
        """
        pass

    @abstractmethod
    def exists_by_txid(self, txid: TxId) -> bool:
        """
        Check if transaction exists by external transaction ID.

        Args:
            txid: External transaction ID to check

        Returns:
            True if transaction exists, False otherwise
        """
        pass

    @abstractmethod
    def get_all_active(self) -> list[Transaction]:
        """
        Get all active transactions.

        Returns:
            List of active transaction entities
        """
        pass

    @abstractmethod
    def get_filtered_queryset(
        self, is_active: bool = None, wallet_ids: list[WalletId] = None
    ):
        """
        Get filtered queryset for pagination.

        Args:
            is_active: Optional boolean filter for active status
            wallet_ids: Optional list of wallet IDs to filter by

        Returns:
            Django QuerySet for pagination
        """
        pass
