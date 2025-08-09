"""
Transaction application commands.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from uuid import UUID

from src.domain.shared.types import Money, WalletId
from src.domain.transactions.entities import Transaction


@dataclass
class CreateTransactionCommand:
    """
    Command for creating a new transaction.
    """

    wallet_id_str: str
    amount_str: str

    def __post_init__(self) -> None:
        """Validate command data after initialization."""
        if not self.wallet_id_str or len(self.wallet_id_str.strip()) == 0:
            raise ValueError("Wallet ID cannot be empty")

        if not self.amount_str or len(self.amount_str.strip()) == 0:
            raise ValueError("Amount cannot be empty")

        # Validate amount format
        try:
            amount_decimal = Decimal(self.amount_str)
        except (InvalidOperation, ValueError) as err:
            raise ValueError("Amount must be a valid number") from err

        # Validate amount is not zero
        if amount_decimal == 0:
            raise ValueError("Amount cannot be zero")

    @property
    def wallet_id(self) -> WalletId:
        """Get wallet ID as domain type."""
        try:
            return WalletId(UUID(self.wallet_id_str))
        except ValueError as err:
            raise ValueError(f"Invalid wallet ID format: {self.wallet_id_str}") from err

    @property
    def amount(self) -> Money:
        """Get amount as domain type."""
        return Money(Decimal(self.amount_str))


class CreateTransactionUseCase:
    """
    Use case for creating a new transaction.
    """

    def __init__(
        self,
        wallet_transaction_orchestration_service,
    ) -> None:
        """
        Initialize use case.

        Args:
            wallet_transaction_orchestration_service: Service for coordinating wallet and transaction operations
        """
        self._wallet_transaction_orchestration_service = (
            wallet_transaction_orchestration_service
        )

    def execute(self, command: CreateTransactionCommand) -> Transaction:
        """
        Execute the use case.

        Args:
            command: Command containing transaction data

        Returns:
            Created transaction entity

        Raises:
            ValueError: If data validation fails
            DomainException: If domain business rules are violated
        """
        # Create transaction and update wallet balance atomically
        (
            transaction,
            updated_wallet,
        ) = self._wallet_transaction_orchestration_service.create_transaction_with_balance_update(
            wallet_id=command.wallet_id,
            amount=command.amount,
        )

        return transaction
