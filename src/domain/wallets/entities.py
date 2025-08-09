"""
Wallet domain entity.
"""
from datetime import datetime

from src.domain.shared.exceptions import (
    WalletAlreadyDeactivatedException,
)
from src.domain.shared.types import Money, WalletId
from src.domain.transactions.entities import Transaction


class Wallet:
    """
    Wallet domain entity.

    This is a pure domain entity with no dependencies on Django or any other framework.
    """

    def __init__(
        self,
        id: WalletId,
        label: str,
        balance: Money,
        is_active: bool = True,
        deactivated_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """
        Initialize a Wallet entity.

        Args:
            id: Unique identifier for the wallet
            label: Human-readable label for the wallet
            balance: Current balance of the wallet
            is_active: Whether the wallet is active
            deactivated_at: Timestamp when wallet was deactivated
            created_at: Timestamp when wallet was created
            updated_at: Timestamp when wallet was last updated
        """
        self._id = id
        self._label = label
        self._balance = balance
        self._is_active = is_active
        self._deactivated_at = deactivated_at
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        self._transactions: list[Transaction] = []

    @property
    def id(self) -> WalletId:
        """Get wallet ID."""
        return self._id

    @property
    def label(self) -> str:
        """Get wallet label."""
        return self._label

    @property
    def balance(self) -> Money:
        """Get wallet balance."""
        return self._balance

    @property
    def is_active(self) -> bool:
        """Check if wallet is active."""
        return self._is_active

    @property
    def deactivated_at(self) -> datetime | None:
        """Get deactivation timestamp."""
        return self._deactivated_at

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at

    @property
    def transactions(self) -> list[Transaction]:
        """Get list of transactions."""
        return self._transactions.copy()

    def update_label(self, new_label: str) -> None:
        """
        Update wallet label.

        Args:
            new_label: New label for the wallet
        """
        if not new_label.strip():
            raise ValueError("Label cannot be empty")

        self._label = new_label.strip()
        self._updated_at = datetime.utcnow()

    def add_transaction(self, transaction: Transaction) -> None:
        """
        Add a transaction to the wallet.

        Note:
            This method only adds the transaction to the wallet's transaction list.
            Balance calculation and validation happens in the infrastructure layer
            within the atomic transaction to prevent race conditions.
        """
        if not self._is_active:
            raise WalletAlreadyDeactivatedException(
                "Cannot add transaction to deactivated wallet"
            )

        # Add transaction to the list (balance will be calculated in infrastructure layer)
        self._transactions.append(transaction)
        self._updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """
        Deactivate the wallet and all its transactions.

        Raises:
            WalletAlreadyDeactivatedException: If wallet is already deactivated
        """
        if not self._is_active:
            raise WalletAlreadyDeactivatedException("Wallet is already deactivated")

        self._is_active = False
        self._deactivated_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

        # Deactivate all transactions
        for transaction in self._transactions:
            if transaction.is_active:
                transaction.deactivate()

    def get_active_transactions(self) -> list[Transaction]:
        """
        Get all active transactions for this wallet.

        Returns:
            List of active transactions
        """
        return [tx for tx in self._transactions if tx.is_active]

    def calculate_balance_from_transactions(self) -> Money:
        """
        Calculate balance by summing all active transactions.

        Returns:
            Calculated balance
        """
        return sum(tx.amount for tx in self.get_active_transactions())

    def __eq__(self, other: object) -> bool:
        """Check equality with another wallet."""
        if not isinstance(other, Wallet):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Get hash of wallet."""
        return hash(self._id)

    def __repr__(self) -> str:
        """Get string representation."""
        return f"Wallet(id={self._id}, label='{self._label}', balance={self._balance}, active={self._is_active})"
