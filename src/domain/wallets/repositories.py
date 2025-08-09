"""
Wallet repository interface.
"""
from abc import ABC, abstractmethod

from src.domain.shared.types import WalletId
from src.domain.transactions.entities import Transaction
from src.domain.wallets.entities import Wallet


class WalletRepository(ABC):
    """
    Abstract wallet repository interface.

    This follows the dependency inversion principle - the domain depends on abstractions,
    not concrete implementations.
    """

    @abstractmethod
    def get_by_id(self, wallet_id: WalletId) -> Wallet | None:
        """
        Get wallet by ID.

        Args:
            wallet_id: Wallet ID to find

        Returns:
            Wallet entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_active_by_id(self, wallet_id: WalletId) -> Wallet | None:
        """
        Get active wallet by ID.

        Args:
            wallet_id: Wallet ID to find

        Returns:
            Active wallet entity if found, None otherwise
        """
        pass

    @abstractmethod
    def save(self, wallet: Wallet) -> Wallet:
        """
        Save wallet entity.

        Args:
            wallet: Wallet entity to save

        Returns:
            Saved wallet entity
        """
        pass

    @abstractmethod
    def get_all_active(self) -> list[Wallet]:
        """
        Get all active wallets.

        Returns:
            List of active wallet entities
        """
        pass

    @abstractmethod
    def get_all_inactive(self) -> list[Wallet]:
        """
        Get all inactive wallets.

        Returns:
            List of inactive wallet entities
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Wallet]:
        """
        Get all wallets.

        Returns:
            List of all wallet entities
        """
        pass

    @abstractmethod
    def get_by_ids(self, wallet_ids: list[WalletId]) -> list[Wallet]:
        """
        Get wallets by IDs.

        Args:
            wallet_ids: List of wallet IDs to find

        Returns:
            List of wallet entities
        """
        pass

    @abstractmethod
    def filter_wallets(
        self,
        is_active: bool | None = None,
        wallet_ids: list[WalletId] | None = None,
    ) -> list[Wallet]:
        """
        Filter wallets by active status and/or wallet IDs.

        Args:
            is_active: Optional boolean filter for active status
            wallet_ids: Optional list of wallet IDs to filter by

        Returns:
            List of filtered wallet entities
        """
        pass

    @abstractmethod
    def get_filtered_queryset(
        self,
        is_active: bool | None = None,
        wallet_ids: list[WalletId] | None = None,
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

    @abstractmethod
    def update_balance_with_transaction(
        self, wallet: Wallet, transaction: Transaction
    ) -> Wallet:
        """
        Update wallet balance atomically with transaction creation.

        Args:
            wallet: Wallet entity with updated balance
            transaction: Transaction entity to save

        Returns:
            Updated wallet entity

        Note:
            This method should be implemented to ensure atomicity between
            wallet balance update and transaction creation.
        """
        pass

    @abstractmethod
    def exists(self, wallet_id: WalletId) -> bool:
        """
        Check if wallet exists.

        Args:
            wallet_id: Wallet ID to check

        Returns:
            True if wallet exists, False otherwise
        """
        pass

    @abstractmethod
    def get_paginated_and_filtered_wallets(
        self,
        is_active: bool | None = None,
        wallet_ids: list[WalletId] | None = None,
        page_number: int = 1,
        page_size: int = 20,
        ordering: str | None = None,
    ):
        pass
