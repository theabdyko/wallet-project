"""
Wallet application queries (use cases) for read operations.
"""
from dataclasses import dataclass
from uuid import UUID

from src.application.services import WalletApplicationService
from src.domain.shared.types import WalletId
from src.domain.wallets.entities import Wallet
from src.domain.wallets.repositories import WalletRepository


@dataclass
class GetWalletQuery:
    """Query to get wallet by ID."""

    wallet_id: WalletId


@dataclass
class GetWalletsByIdsQuery:
    """Query to get wallets by IDs."""

    wallet_ids: list[WalletId]


@dataclass
class GetAllActiveWalletsQuery:
    """Query to get all active wallets."""

    pass


@dataclass
class ListWalletsQuery:
    """Query to list wallets with optional filters."""

    wallet_ids_str: list[str] | None = None
    is_active_str: str | None = None


@dataclass
class ListWalletsWithPaginationQuery:
    """Query to list wallets with pagination support."""

    wallet_ids_str: list[str] | None = None
    is_active_str: str | None = None


@dataclass
class ListWalletsWithDatabasePaginationQuery:
    """Query to list wallets with database-level pagination and filtering."""

    wallet_ids_str: list[str] | None = None
    is_active_str: str | None = None
    page_number: int = 1
    page_size: int = 20
    ordering: str | None = None


class GetWalletUseCase:
    """
    Use case for getting wallet by ID.
    """

    def __init__(self, wallet_application_service: WalletApplicationService) -> None:
        """
        Initialize use case.

        Args:
            wallet_application_service: Wallet application service
        """
        self._wallet_application_service = wallet_application_service

    def execute(self, query: GetWalletQuery) -> Wallet:
        """
        Execute the use case.

        Args:
            query: Query containing wallet ID

        Returns:
            Wallet entity
        """
        return self._wallet_application_service.get_wallet(query.wallet_id)


class GetWalletsByIdsUseCase:
    """
    Use case for getting wallets by IDs.
    """

    def __init__(self, wallet_application_service: WalletApplicationService) -> None:
        """
        Initialize use case.

        Args:
            wallet_application_service: Wallet application service
        """
        self._wallet_application_service = wallet_application_service

    def execute(self, query: GetWalletsByIdsQuery) -> list[Wallet]:
        """
        Execute the use case.

        Args:
            query: Query containing list of wallet IDs

        Returns:
            List of wallet entities
        """
        return self._wallet_application_service.get_wallets_by_ids(query.wallet_ids)


class GetAllActiveWalletsUseCase:
    """
    Use case for getting all active wallets.
    """

    def __init__(self, wallet_application_service: WalletApplicationService) -> None:
        """
        Initialize use case.

        Args:
            wallet_application_service: Wallet application service
        """
        self._wallet_application_service = wallet_application_service

    def execute(self, query: GetAllActiveWalletsQuery) -> list[Wallet]:
        """
        Execute the use case.

        Args:
            query: Query for all active wallets

        Returns:
            List of active wallet entities
        """
        return self._wallet_application_service.list_wallets(is_active=True)


class ListWalletsUseCase:
    """
    Use case for listing wallets with optional filters.
    """

    def __init__(self, wallet_application_service: WalletApplicationService) -> None:
        """
        Initialize use case.

        Args:
            wallet_application_service: Wallet application service
        """
        self._wallet_application_service = wallet_application_service

    def execute(self, query: ListWalletsQuery) -> list[Wallet]:
        """
        Execute the use case.

        Args:
            query: Query with optional filters as strings

        Returns:
            List of wallet entities

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

        # Parse and validate is_active filter if provided
        is_active = None
        if query.is_active_str is not None:
            if query.is_active_str.lower() in ("true", "1", "yes"):
                is_active = True
            elif query.is_active_str.lower() in ("false", "0", "no"):
                is_active = False
            else:
                raise ValueError("is_active filter must be 'true' or 'false'")

        # Use the new filtering method that handles multiple filters together
        return self._wallet_application_service.list_wallets(
            is_active=is_active, wallet_ids=wallet_ids
        )


class ListWalletsWithPaginationUseCase:
    """
    Use case for listing wallets with pagination support.

    This use case returns a Django QuerySet for pagination instead of a list of entities.
    """

    def __init__(self, wallet_repository: WalletRepository) -> None:
        """
        Initialize use case.

        Args:
            wallet_repository: Wallet repository for data access
        """
        self._wallet_repository = wallet_repository

    def execute(self, query: ListWalletsWithPaginationQuery):
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
        return self._wallet_repository.get_filtered_queryset(
            is_active=is_active, wallet_ids=wallet_ids
        )


class ListWalletsWithDatabasePaginationUseCase:
    """
    Use case for listing wallets with database-level pagination and filtering.

    This use case implements efficient database-level pagination and filtering
    to avoid loading unnecessary data into memory.
    """

    def __init__(self, wallet_repository: WalletRepository) -> None:
        """
        Initialize use case.

        Args:
            wallet_repository: Wallet repository for data access
        """
        self._wallet_repository = wallet_repository

    def execute(self, query: ListWalletsWithDatabasePaginationQuery):
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
        return self._wallet_repository.get_paginated_and_filtered_wallets(
            is_active=is_active,
            wallet_ids=wallet_ids,
            page_number=query.page_number,
            page_size=query.page_size,
            ordering=query.ordering,
        )
