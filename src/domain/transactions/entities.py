"""
Transaction domain entity.
"""
from datetime import datetime

from src.domain.shared.exceptions import TransactionAlreadyDeactivatedException
from src.domain.shared.types import Money, TransactionId, TxId, WalletId


class Transaction:
    """
    Transaction domain entity.

    This is a pure domain entity with no dependencies on Django or any other framework.
    """

    def __init__(
        self,
        id: TransactionId,
        wallet_id: WalletId,
        txid: TxId,
        amount: Money,
        is_active: bool = True,
        deactivated_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """
        Initialize a Transaction entity.

        Args:
            id: Unique identifier for the transaction
            wallet_id: ID of the wallet this transaction belongs to
            txid: External transaction ID
            amount: Transaction amount (positive for credits, negative for debits)
            is_active: Whether the transaction is active
            deactivated_at: Timestamp when transaction was deactivated
            created_at: Timestamp when transaction was created
            updated_at: Timestamp when transaction was last updated
        """
        self._id = id
        self._wallet_id = wallet_id
        self._txid = txid
        self._amount = amount
        self._is_active = is_active
        self._deactivated_at = deactivated_at
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()

    @property
    def id(self) -> TransactionId:
        """Get transaction ID."""
        return self._id

    @property
    def wallet_id(self) -> WalletId:
        """Get wallet ID."""
        return self._wallet_id

    @property
    def txid(self) -> TxId:
        """Get external transaction ID."""
        return self._txid

    @property
    def amount(self) -> Money:
        """Get transaction amount."""
        return self._amount

    @property
    def is_active(self) -> bool:
        """Check if transaction is active."""
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

    def deactivate(self) -> None:
        """
        Deactivate the transaction.

        Raises:
            TransactionAlreadyDeactivatedException: If transaction is already deactivated
        """
        if not self._is_active:
            raise TransactionAlreadyDeactivatedException(
                "Transaction is already deactivated"
            )

        self._is_active = False
        self._deactivated_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    def is_credit(self) -> bool:
        """
        Check if transaction is a credit (positive amount).

        Returns:
            True if credit, False if debit
        """
        return self._amount > 0

    def is_debit(self) -> bool:
        """
        Check if transaction is a debit (negative amount).

        Returns:
            True if debit, False if credit
        """
        return self._amount < 0

    def __eq__(self, other: object) -> bool:
        """Check equality with another transaction."""
        if not isinstance(other, Transaction):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Get hash of transaction."""
        return hash(self._id)

    def __repr__(self) -> str:
        """Get string representation."""
        return f"Transaction(id={self._id}, wallet_id={self._wallet_id}, txid='{self._txid}', amount={self._amount}, active={self._is_active})"
