"""
Service dependency injection containers.
"""
from dependency_injector import containers, providers

from src.application.services import (
    TransactionApplicationService,
    WalletApplicationService,
    WalletTransactionOrchestrationService,
)
from src.domain.transactions.services import TransactionDomainService
from src.domain.wallets.services import WalletDomainService
from src.infrastructure.transactions.repositories import DjangoTransactionRepository
from src.infrastructure.wallets.repositories import DjangoWalletRepository


class ServiceContainer(containers.DeclarativeContainer):
    """
    Service dependency injection container.

    This container manages all service dependencies for the application.
    """

    # Infrastructure Layer - Repositories
    wallet_repository = providers.Singleton(DjangoWalletRepository)
    transaction_repository = providers.Singleton(DjangoTransactionRepository)

    # Domain Layer - Services
    wallet_domain_service = providers.Factory(
        WalletDomainService,
        wallet_repository=wallet_repository,
    )

    transaction_domain_service = providers.Factory(
        TransactionDomainService,
        transaction_repository=transaction_repository,
    )

    # Application Layer - Services
    wallet_application_service = providers.Factory(
        WalletApplicationService,
        wallet_domain_service=wallet_domain_service,
    )

    transaction_application_service = providers.Factory(
        TransactionApplicationService,
        transaction_domain_service=transaction_domain_service,
    )

    wallet_transaction_orchestration_service = providers.Factory(
        WalletTransactionOrchestrationService,
        wallet_domain_service=wallet_domain_service,
        transaction_domain_service=transaction_domain_service,
    )
