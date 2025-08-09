"""
Repository dependency injection containers.
"""
from dependency_injector import containers, providers

from src.infrastructure.transactions.repositories import DjangoTransactionRepository
from src.infrastructure.wallets.repositories import DjangoWalletRepository


class RepositoryContainer(containers.DeclarativeContainer):
    """
    Repository dependency injection container.

    This container manages all repository dependencies for the application.
    """

    # Infrastructure Layer - Repositories
    wallet_repository = providers.Singleton(DjangoWalletRepository)
    transaction_repository = providers.Singleton(DjangoTransactionRepository)

    # Class methods for direct access
    @classmethod
    def wallet_repository(cls):
        """Get wallet repository instance."""
        return cls.wallet_repository()

    @classmethod
    def transaction_repository(cls):
        """Get transaction repository instance."""
        return cls.transaction_repository()
