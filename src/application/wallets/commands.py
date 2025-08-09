"""
Wallet application commands (use cases) for write operations.
"""
from dataclasses import dataclass
from uuid import UUID

from src.application.services import (
    WalletApplicationService,
    WalletTransactionOrchestrationService,
)
from src.domain.shared.types import WalletId
from src.domain.wallets.entities import Wallet


@dataclass
class UpdateWalletLabelCommand:
    """Command to update wallet label."""

    wallet_id_str: str
    new_label: str


@dataclass
class DeactivateWalletCommand:
    """Command to deactivate wallet."""

    wallet_id_str: str


@dataclass
class CreateWalletCommand:
    """Command to create wallet."""

    label: str


class UpdateWalletLabelUseCase:
    """
    Use case for updating wallet label.
    """

    def __init__(self, wallet_application_service: WalletApplicationService) -> None:
        """
        Initialize use case.

        Args:
            wallet_application_service: Wallet application service
        """
        self._wallet_application_service = wallet_application_service

    def execute(self, command: UpdateWalletLabelCommand) -> Wallet:
        """
        Execute the use case.

        Args:
            command: Command containing wallet ID string and new label

        Returns:
            Updated wallet entity

        Raises:
            ValueError: If wallet ID is not a valid UUID
            DomainException: If wallet not found or other domain errors
        """
        # Validate wallet ID format
        try:
            wallet_uuid = UUID(command.wallet_id_str)
        except ValueError as err:
            raise ValueError("Invalid wallet ID format") from err

        wallet_id = WalletId(wallet_uuid)

        # Validate label
        if not command.new_label or len(command.new_label.strip()) == 0:
            raise ValueError("Label cannot be empty")

        if len(command.new_label) > 255:
            raise ValueError("Label cannot exceed 255 characters")

        return self._wallet_application_service.update_wallet_label(
            wallet_id, command.new_label.strip()
        )


class DeactivateWalletUseCase:
    """
    Use case for deactivating wallet and all its transactions.
    """

    def __init__(
        self,
        wallet_transaction_orchestration_service: WalletTransactionOrchestrationService,
    ) -> None:
        """
        Initialize use case.

        Args:
            wallet_transaction_orchestration_service: Service for coordinating wallet and transaction operations
        """
        self._wallet_transaction_orchestration_service = (
            wallet_transaction_orchestration_service
        )

    def execute(self, command: DeactivateWalletCommand) -> Wallet:
        """
        Execute the use case.

        Args:
            command: Command containing wallet ID string to deactivate

        Returns:
            Deactivated wallet entity

        Raises:
            ValueError: If wallet ID is not a valid UUID
            DomainException: If wallet not found or other domain errors
        """
        # Validate wallet ID format
        try:
            wallet_uuid = UUID(command.wallet_id_str)
        except ValueError as err:
            raise ValueError("Invalid wallet ID format") from err

        wallet_id = WalletId(wallet_uuid)

        # Deactivate wallet and all its transactions atomically
        return self._wallet_transaction_orchestration_service.deactivate_wallet_with_transactions(
            wallet_id
        )


class CreateWalletUseCase:
    """
    Use case for creating a new wallet.
    """

    def __init__(self, wallet_application_service: WalletApplicationService) -> None:
        """
        Initialize use case.

        Args:
            wallet_application_service: Wallet application service
        """
        self._wallet_application_service = wallet_application_service

    def execute(self, command: CreateWalletCommand) -> Wallet:
        """
        Execute the use case.

        Args:
            command: Command containing wallet data

        Returns:
            Created wallet entity

        Raises:
            ValueError: If data validation fails
            DomainException: If domain business rules are violated
        """
        # Validate label
        if not command.label or len(command.label.strip()) == 0:
            raise ValueError("Label cannot be empty")

        if len(command.label) > 255:
            raise ValueError("Label cannot exceed 255 characters")

        return self._wallet_application_service.create_wallet(
            label=command.label.strip(),
        )
