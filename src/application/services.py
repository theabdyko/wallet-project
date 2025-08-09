"""
Application services for coordinating domain operations.
"""
from uuid import uuid4

from src.domain.shared.types import Money, TxId, WalletId
from src.domain.transactions.entities import Transaction
from src.domain.transactions.services import TransactionDomainService
from src.domain.wallets.entities import Wallet
from src.domain.wallets.services import WalletDomainService


class WalletApplicationService:
    """
    Application service for wallet-only operations.

    This service handles wallet-specific business logic that doesn't involve transactions.
    """

    def __init__(self, wallet_domain_service: WalletDomainService) -> None:
        """
        Initialize wallet application service.

        Args:
            wallet_domain_service: Wallet domain service
        """
        self._wallet_domain_service = wallet_domain_service

    def create_wallet(self, label: str) -> Wallet:
        """
        Create a wallet with 0 balance.

        Args:
            label: Wallet label

        Returns:
            Created wallet entity
        """
        return self._wallet_domain_service.create_wallet(label)

    def update_wallet_label(self, wallet_id: WalletId, new_label: str) -> Wallet:
        """
        Update wallet label.

        Args:
            wallet_id: Wallet ID to update
            new_label: New label for the wallet

        Returns:
            Updated wallet entity
        """
        wallet = self._wallet_domain_service.get_wallet(wallet_id)
        wallet.update_label(new_label)
        return self._wallet_domain_service.save_wallet(wallet)

    def deactivate_wallet(self, wallet_id: WalletId) -> Wallet:
        """
        Deactivate a wallet.

        Args:
            wallet_id: Wallet ID to deactivate

        Returns:
            Deactivated wallet entity
        """
        wallet = self._wallet_domain_service.get_wallet(wallet_id)
        wallet.deactivate()
        return self._wallet_domain_service.save_wallet(wallet)

    def get_wallet(self, wallet_id: WalletId) -> Wallet:
        """
        Get wallet by ID.

        Args:
            wallet_id: Wallet ID to get

        Returns:
            Wallet entity
        """
        return self._wallet_domain_service.get_wallet(wallet_id)

    def get_wallets_by_ids(self, wallet_ids: list[WalletId]) -> list[Wallet]:
        """
        Get wallets by IDs.

        Args:
            wallet_ids: List of wallet IDs to get

        Returns:
            List of wallet entities
        """
        return self._wallet_domain_service.get_wallets_by_ids(wallet_ids)

    def list_wallets(
        self, is_active: bool = None, wallet_ids: list[WalletId] = None
    ) -> list[Wallet]:
        """
        List wallets with optional filtering.

        Args:
            is_active: Optional boolean filter for active status
            wallet_ids: Optional list of wallet IDs to filter by

        Returns:
            List of filtered wallet entities
        """
        return self._wallet_domain_service.filter_wallets(is_active, wallet_ids)


class TransactionApplicationService:
    """
    Application service for transaction-only operations.

    This service handles transaction-specific business logic that doesn't involve wallets.
    """

    def __init__(self, transaction_domain_service: TransactionDomainService) -> None:
        """
        Initialize transaction application service.

        Args:
            transaction_domain_service: Transaction domain service
        """
        self._transaction_domain_service = transaction_domain_service

    def get_transaction_by_txid(self, txid: TxId) -> Transaction:
        """
        Get transaction by external transaction ID.

        Args:
            txid: External transaction ID to find

        Returns:
            Transaction entity if found

        Raises:
            ValueError: If transaction not found
        """
        transaction = self._transaction_domain_service.get_transaction_by_txid(txid)
        if not transaction:
            raise ValueError(f"Transaction with txid {txid} not found")
        return transaction

    def get_transactions_by_wallet_id(self, wallet_id: WalletId) -> list[Transaction]:
        """
        Get all transactions for a wallet.

        Args:
            wallet_id: Wallet ID to get transactions for

        Returns:
            List of transaction entities
        """
        return self._transaction_domain_service.get_transactions_by_wallet_id(wallet_id)

    def get_transactions_by_wallet_ids(
        self, wallet_ids: list[WalletId]
    ) -> list[Transaction]:
        """
        Get all transactions for multiple wallets.

        Args:
            wallet_ids: List of wallet IDs to get transactions for

        Returns:
            List of transaction entities
        """
        return self._transaction_domain_service.get_transactions_by_wallet_ids(
            wallet_ids
        )

    def list_transactions(self) -> list[Transaction]:
        """
        List all active transactions.

        Returns:
            List of active transaction entities
        """
        return self._transaction_domain_service.get_all_active()


class WalletTransactionOrchestrationService:
    """
    Application service for operations that span both wallet and transaction domains.

    This service coordinates complex business logic that involves both wallets and transactions.
    """

    def __init__(
        self,
        wallet_domain_service: WalletDomainService,
        transaction_domain_service: TransactionDomainService,
    ) -> None:
        """
        Initialize wallet-transaction orchestration service.

        Args:
            wallet_domain_service: Wallet domain service
            transaction_domain_service: Transaction domain service
        """
        self._wallet_domain_service = wallet_domain_service
        self._transaction_domain_service = transaction_domain_service

    def create_wallet_with_initial_balance(
        self,
        label: str,
        initial_balance: Money,
        initial_txid: TxId,
    ) -> Wallet:
        """
        Create a wallet with an initial balance transaction.

        Args:
            label: Wallet label
            initial_balance: Initial balance amount
            initial_txid: External transaction ID for the initial balance

        Returns:
            Created wallet entity
        """
        # Create wallet
        wallet = Wallet(
            id=WalletId(uuid4()),
            label=label,
            balance=initial_balance,
        )

        # Create initial transaction
        transaction = self._transaction_domain_service.create_transaction(
            wallet_id=wallet.id,
            txid=initial_txid,
            amount=initial_balance,
        )

        # Add transaction to wallet
        wallet.add_transaction(transaction)

        return wallet

    def deactivate_wallet_with_transactions(self, wallet_id: WalletId) -> Wallet:
        """
        Deactivate wallet and all its transactions atomically.

        Args:
            wallet_id: Wallet ID to deactivate

        Returns:
            Deactivated wallet entity
        """
        # Get wallet and all its transactions
        wallet = self._wallet_domain_service.get_wallet(wallet_id)
        transactions = self._transaction_domain_service.get_transactions_by_wallet_id(
            wallet_id
        )

        # Add transactions to wallet for deactivation
        for transaction in transactions:
            wallet._transactions.append(transaction)

        # Deactivate wallet (this will also deactivate all transactions)
        wallet.deactivate()

        return wallet

    def get_wallet_with_transactions(
        self, wallet_id: WalletId
    ) -> tuple[Wallet, list[Transaction]]:
        """
        Get wallet with all its active transactions.

        Args:
            wallet_id: Wallet ID to get

        Returns:
            Tuple of (wallet, transactions)
        """
        wallet = self._wallet_domain_service.get_wallet(wallet_id)
        transactions = self._transaction_domain_service.get_transactions_by_wallet_id(
            wallet_id
        )

        return wallet, transactions

    def create_transaction_with_balance_update(
        self,
        wallet_id: WalletId,
        amount: Money,
    ) -> tuple[Transaction, Wallet]:
        """
        Create a transaction and update wallet balance atomically.

        Args:
            wallet_id: ID of the wallet to create transaction for
            amount: Transaction amount

        Returns:
            Tuple of (created_transaction, updated_wallet)

        Raises:
            ValueError: If wallet is deactivated or business rules are violated
            InsufficientBalanceException: If transaction would result in negative balance
        """
        # Get the wallet
        wallet = self._wallet_domain_service.get_wallet(wallet_id)

        # Check if wallet is active
        if not wallet.is_active:
            raise ValueError("Cannot create transaction for deactivated wallet")

        # Create transaction entity (not yet persisted)
        transaction = self._transaction_domain_service.create_transaction(
            wallet_id=wallet_id,
            amount=amount,
        )

        # Add transaction to wallet (balance calculation happens in infrastructure layer)
        wallet.add_transaction(transaction)

        # Persist both transaction and wallet balance update atomically
        # Balance validation and calculation happens within the atomic transaction
        updated_wallet = self._wallet_domain_service.update_balance_with_transaction(
            wallet, transaction
        )

        return transaction, updated_wallet
