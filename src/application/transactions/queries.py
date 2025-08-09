"""
Transaction application queries (use cases) for read operations.
"""
from dataclasses import dataclass
from uuid import UUID

from src.application.services import TransactionApplicationService
from src.domain.shared.types import TxId, WalletId
from src.domain.transactions.entities import Transaction
from src.domain.transactions.repositories import TransactionRepository


@dataclass
class GetTransactionByTxidQuery:
    """Query to get transaction by external transaction ID."""

    txid_str: str


@dataclass
class GetTransactionsByWalletIdQuery:
    """Query to get transactions by wallet ID."""

    wallet_id: WalletId


@dataclass
class ListTransactionsQuery:
    """Query to list transactions with optional filters."""

    wallet_ids_str: list[str] | None = None


@dataclass
class ListTransactionsWithPaginationQuery:
    """Query to list transactions with pagination support."""

    wallet_ids_str: list[str] | None = None
    is_active_str: str | None = None


@dataclass
class ListTransactionsWithDatabasePaginationQuery:
    """Query to list transactions with database-level pagination and filtering."""

    wallet_ids_str: list[str] | None = None
    is_active_str: str | None = None
    page_number: int = 1
    page_size: int = 20
    ordering: str | None = None


class GetTransactionByTxidUseCase:
    """
    Use case for getting transaction by external transaction ID.
    """

    def __init__(
        self, transaction_application_service: TransactionApplicationService
    ) -> None:
        """
        Initialize use case.

        Args:
            transaction_application_service: Transaction application service
        """
        self._transaction_application_service = transaction_application_service

    def execute(self, query: GetTransactionByTxidQuery) -> Transaction:
        """
        Execute the use case.

        Args:
            query: Query containing external transaction ID string

        Returns:
            Transaction entity

        Raises:
            ValueError: If txid validation fails
            DomainException: If transaction not found or other domain errors
        """
        # Validate txid
        if not query.txid_str or len(query.txid_str.strip()) == 0:
            raise ValueError("Transaction ID cannot be empty")

        if len(query.txid_str) > 255:
            raise ValueError("Transaction ID cannot exceed 255 characters")

        txid = TxId(query.txid_str.strip())

        return self._transaction_application_service.get_transaction_by_txid(txid)


class GetTransactionsByWalletIdUseCase:
    """
    Use case for getting transactions by wallet ID.
    """

    def __init__(
        self, transaction_application_service: TransactionApplicationService
    ) -> None:
        """
        Initialize use case.

        Args:
            transaction_application_service: Transaction application service
        """
        self._transaction_application_service = transaction_application_service

    def execute(self, query: GetTransactionsByWalletIdQuery) -> list[Transaction]:
        """
        Execute the use case.

        Args:
            query: Query containing wallet ID

        Returns:
            List of transaction entities
        """
        return self._transaction_application_service.get_transactions_by_wallet_id(
            query.wallet_id
        )


class ListTransactionsUseCase:
    """
    Use case for listing transactions with optional filters.
    """

    def __init__(
        self, transaction_application_service: TransactionApplicationService
    ) -> None:
        """
        Initialize use case.

        Args:
            transaction_application_service: Transaction application service
        """
        self._transaction_application_service = transaction_application_service

    def execute(self, query: ListTransactionsQuery) -> list[Transaction]:
        """
        Execute the use case.

        Args:
            query: Query with optional filters as strings

        Returns:
            List of transaction entities

        Raises:
            ValueError: If data validation fails
            DomainException: If domain business rules are violated
        """
        # Parse and validate wallet IDs if provided
        wallet_ids = None
        if query.wallet_ids_str:
            try:
                wallet_ids = [
                    WalletId(UUID(wallet_id_str))
                    for wallet_id_str in query.wallet_ids_str
                ]
            except ValueError as err:
                raise ValueError("Invalid wallet ID format in wallet_ids filter") from err

        return self._transaction_application_service.list_transactions(
            wallet_ids=wallet_ids
        )


class ListTransactionsWithPaginationUseCase:
    """
    Use case for listing transactions with pagination support.

    This use case returns a Django QuerySet for pagination instead of a list of entities.
    """

    def __init__(self, transaction_repository: TransactionRepository) -> None:
        """
        Initialize use case.

        Args:
            transaction_repository: Transaction repository for data access
        """
        self._transaction_repository = transaction_repository

    def execute(self, query: ListTransactionsWithPaginationQuery):
        """
        Execute the use case.

        Args:
            query: Query with optional filters as strings

        Returns:
            Django QuerySet for pagination

        Raises:
            ValueError: If data validation fails
        """
        # Parse and validate wallet IDs if provided
        wallet_ids = None
        if query.wallet_ids_str:
            try:
                wallet_ids = [
                    WalletId(UUID(wallet_id_str))
                    for wallet_id_str in query.wallet_ids_str
                ]
            except ValueError as err:
                raise ValueError("Invalid wallet ID format in wallet_ids filter") from err

        # Parse and validate is_active filter if provided
        is_active = None
        if query.is_active_str is not None:
            if query.is_active_str.lower() in ("true", "1", "yes"):
                is_active = True
            elif query.is_active_str.lower() in ("false", "0", "no"):
                is_active = False
            else:
                raise ValueError("is_active filter must be 'true' or 'false'")

        # Return queryset for pagination
        return self._transaction_repository.get_filtered_queryset(
            is_active=is_active, wallet_ids=wallet_ids
        )


class ListTransactionsWithDatabasePaginationUseCase:
    """
    Use case for listing transactions with database-level pagination and filtering.

    This use case implements efficient database-level pagination and filtering
    to avoid loading unnecessary data into memory.
    """

    def __init__(self, transaction_repository: TransactionRepository) -> None:
        """
        Initialize use case.

        Args:
            transaction_repository: Transaction repository for data access
        """
        self._transaction_repository = transaction_repository

    def execute(self, query: ListTransactionsWithDatabasePaginationQuery):
        """
        Execute the use case with database-level pagination and filtering.

        Args:
            query: Query with filters and pagination parameters

        Returns:
            Dictionary containing paginated data and metadata

        Raises:
            ValueError: If data validation fails
        """
        # Parse and validate wallet IDs if provided
        wallet_ids = None
        if query.wallet_ids_str:
            try:
                wallet_ids = [
                    WalletId(UUID(wallet_id_str))
                    for wallet_id_str in query.wallet_ids_str
                ]
            except ValueError as err:
                raise ValueError("Invalid wallet ID format in wallet_ids filter") from err

        # Parse and validate is_active filter if provided
        is_active = None
        if query.is_active_str is not None:
            if query.is_active_str.lower() in ("true", "1", "yes"):
                is_active = True
            elif query.is_active_str.lower() in ("false", "0", "no"):
                is_active = False
            else:
                raise ValueError("is_active filter must be 'true' or 'false'")

        # Validate pagination parameters
        if query.page_number < 1:
            raise ValueError("Page number must be greater than 0")
        if query.page_size < 1 or query.page_size > 100:
            raise ValueError("Page size must be between 1 and 100")

        # Get paginated and filtered data from repository
        return self._transaction_repository.get_paginated_and_filtered_transactions(
            is_active=is_active,
            wallet_ids=wallet_ids,
            page_number=query.page_number,
            page_size=query.page_size,
            ordering=query.ordering,
        )
