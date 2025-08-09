"""
Use case dependency injection containers.
"""
from dependency_injector import containers, providers

from src.application.transactions.commands import CreateTransactionUseCase
from src.application.transactions.queries import (
    GetTransactionByTxidUseCase,
    GetTransactionsByWalletIdUseCase,
    ListTransactionsUseCase,
    ListTransactionsWithDatabasePaginationUseCase,
    ListTransactionsWithPaginationUseCase,
)
from src.application.wallets.commands import (
    CreateWalletUseCase,
    DeactivateWalletUseCase,
    UpdateWalletLabelUseCase,
)
from src.application.wallets.queries import (
    GetAllActiveWalletsUseCase,
    GetWalletsByIdsUseCase,
    GetWalletUseCase,
    ListWalletsUseCase,
    ListWalletsWithDatabasePaginationUseCase,
    ListWalletsWithPaginationUseCase,
)
from src.containers.services import ServiceContainer


class UseCaseContainer(containers.DeclarativeContainer):
    """
    Use case dependency injection container.

    This container manages all use case dependencies for the application.
    """

    # Command Use Cases
    create_wallet_use_case = providers.Factory(
        CreateWalletUseCase,
        wallet_application_service=ServiceContainer.wallet_application_service,
    )

    create_transaction_use_case = providers.Factory(
        CreateTransactionUseCase,
        wallet_transaction_orchestration_service=ServiceContainer.wallet_transaction_orchestration_service,
    )

    update_wallet_label_use_case = providers.Factory(
        UpdateWalletLabelUseCase,
        wallet_application_service=ServiceContainer.wallet_application_service,
    )

    deactivate_wallet_use_case = providers.Factory(
        DeactivateWalletUseCase,
        wallet_transaction_orchestration_service=ServiceContainer.wallet_transaction_orchestration_service,
    )

    # Query Use Cases - Wallet
    get_wallet_use_case = providers.Factory(
        GetWalletUseCase,
        wallet_application_service=ServiceContainer.wallet_application_service,
    )

    get_wallets_by_ids_use_case = providers.Factory(
        GetWalletsByIdsUseCase,
        wallet_application_service=ServiceContainer.wallet_application_service,
    )

    get_all_active_wallets_use_case = providers.Factory(
        GetAllActiveWalletsUseCase,
        wallet_application_service=ServiceContainer.wallet_application_service,
    )

    list_wallets_use_case = providers.Factory(
        ListWalletsUseCase,
        wallet_application_service=ServiceContainer.wallet_application_service,
    )

    list_wallets_with_pagination_use_case = providers.Factory(
        ListWalletsWithPaginationUseCase,
        wallet_repository=ServiceContainer.wallet_repository,
    )

    list_wallets_with_database_pagination_use_case = providers.Factory(
        ListWalletsWithDatabasePaginationUseCase,
        wallet_repository=ServiceContainer.wallet_repository,
    )

    # Query Use Cases - Transaction
    get_transaction_by_txid_use_case = providers.Factory(
        GetTransactionByTxidUseCase,
        transaction_application_service=ServiceContainer.transaction_application_service,
    )

    get_transactions_by_wallet_id_use_case = providers.Factory(
        GetTransactionsByWalletIdUseCase,
        transaction_application_service=ServiceContainer.transaction_application_service,
    )

    list_transactions_use_case = providers.Factory(
        ListTransactionsUseCase,
        transaction_application_service=ServiceContainer.transaction_application_service,
    )

    list_transactions_with_pagination_use_case = providers.Factory(
        ListTransactionsWithPaginationUseCase,
        transaction_repository=ServiceContainer.transaction_repository,
    )

    list_transactions_with_database_pagination_use_case = providers.Factory(
        ListTransactionsWithDatabasePaginationUseCase,
        transaction_repository=ServiceContainer.transaction_repository,
    )
