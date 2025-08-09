"""
Wallet domain services.
"""
from uuid import uuid4

from src.domain.shared.exceptions import WalletNotFoundException
from src.domain.shared.types import Money, WalletId
from src.domain.transactions.entities import Transaction
from src.domain.wallets.entities import Wallet
from src.domain.wallets.repositories import WalletRepository


class WalletDomainService:
    """
    Wallet domain service for business logic operations.
    """

    def __init__(self, wallet_repository: WalletRepository) -> None:
        """
        Initialize wallet domain service.

        Args:
            wallet_repository: Wallet repository implementation
        """
        self._wallet_repository = wallet_repository

    def create_wallet(self, label: str) -> Wallet:
        """
        Create a new wallet with a default balance of 0.

        Args:
            label: Human-readable label for the wallet

        Returns:
            Newly created wallet entity

        Raises:
            ValueError: If label is empty or invalid
        """
        if not label or not label.strip():
            raise ValueError("Wallet label cannot be empty")

        # Create a new wallet with default balance of 0
        wallet = Wallet(id=WalletId(uuid4()), label=label.strip(), balance=Money(0))

        # Save the wallet to the repository
        return self._wallet_repository.save(wallet)

    def get_wallet(self, wallet_id: WalletId) -> Wallet:
        """
        Get wallet by ID.

        Args:
            wallet_id: Wallet ID to find

        Returns:
            Wallet entity

        Raises:
            WalletNotFoundException: If wallet is not found
        """
        wallet = self._wallet_repository.get_active_by_id(wallet_id)
        if not wallet:
            raise WalletNotFoundException(f"Wallet with ID {wallet_id} not found")
        return wallet

    def update_wallet_label(self, wallet_id: WalletId, new_label: str) -> Wallet:
        """
        Update wallet label.

        Args:
            wallet_id: Wallet ID to update
            new_label: New label for the wallet

        Returns:
            Updated wallet entity

        Raises:
            WalletNotFoundException: If wallet is not found
        """
        wallet = self.get_wallet(wallet_id)
        wallet.update_label(new_label)
        return self._wallet_repository.save(wallet)

    def save_wallet(self, wallet: Wallet) -> Wallet:
        """
        Save wallet to repository.

        Args:
            wallet: Wallet entity to save

        Returns:
            Saved wallet entity
        """
        return self._wallet_repository.save(wallet)

    def deactivate_wallet(self, wallet_id: WalletId) -> Wallet:
        """
        Deactivate wallet and all its transactions.

        Args:
            wallet_id: Wallet ID to deactivate

        Returns:
            Deactivated wallet entity

        Raises:
            WalletNotFoundException: If wallet is not found
        """
        wallet = self.get_wallet(wallet_id)
        wallet.deactivate()
        return self._wallet_repository.save(wallet)

    def get_wallets_by_ids(self, wallet_ids: list[WalletId]) -> list[Wallet]:
        """
        Get wallets by IDs.

        Args:
            wallet_ids: List of wallet IDs to find

        Returns:
            List of wallet entities
        """
        return self._wallet_repository.get_by_ids(wallet_ids)

    def get_all_active_wallets(self) -> list[Wallet]:
        """
        Get all active wallets.

        Returns:
            List of active wallet entities
        """
        return self._wallet_repository.get_all_active()

    def get_all_inactive_wallets(self) -> list[Wallet]:
        """
        Get all inactive wallets.

        Returns:
            List of inactive wallet entities
        """
        return self._wallet_repository.get_all_inactive()

    def get_all_wallets(self) -> list[Wallet]:
        """
        Get all wallets.

        Returns:
            List of all wallet entities
        """
        return self._wallet_repository.get_all()

    def filter_wallets(
        self,
        is_active: bool | None = None,
        wallet_ids: list[WalletId] | None = None,
    ) -> list[Wallet]:
        """
        Filter wallets with multiple optional parameters.

        Args:
            is_active: Optional boolean filter for active status (None = both active and inactive)
            wallet_ids: Optional list of wallet IDs to filter by

        Returns:
            List of filtered wallet entities
        """
        return self._wallet_repository.filter_wallets(is_active, wallet_ids)

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
            This method delegates to the repository to ensure atomicity
            between wallet balance update and transaction creation.
        """
        return self._wallet_repository.update_balance_with_transaction(
            wallet, transaction
        )
