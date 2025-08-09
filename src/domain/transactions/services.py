"""
Transaction domain services.
"""
from uuid import uuid4

from src.domain.shared.exceptions import TransactionNotFoundException
from src.domain.shared.types import Money, TransactionId, TxId, WalletId
from src.domain.transactions.entities import Transaction
from src.domain.transactions.repositories import TransactionRepository


class TransactionDomainService:
    """
    Transaction domain service for business logic operations.
    """

    def __init__(self, transaction_repository: TransactionRepository) -> None:
        """
        Initialize transaction domain service.

        Args:
            transaction_repository: Transaction repository implementation
        """
        self._transaction_repository = transaction_repository

    def get_transaction_by_txid(self, txid: TxId) -> Transaction:
        """
        Get transaction by external transaction ID.

        Args:
            txid: External transaction ID to find

        Returns:
            Transaction entity

        Raises:
            TransactionNotFoundException: If transaction is not found
        """
        transaction = self._transaction_repository.get_active_by_txid(txid)
        if not transaction:
            raise TransactionNotFoundException(
                f"Transaction with txid {txid} not found"
            )
        return transaction

    def create_transaction(
        self,
        wallet_id: WalletId,
        amount: Money,
    ) -> Transaction:
        """
        Create a new transaction with auto-generated txid.

        Args:
            wallet_id: ID of the wallet this transaction belongs to
            amount: Transaction amount

        Returns:
            Created transaction entity (not yet persisted)

        Note:
            This method only creates the transaction entity in memory.
            Persistence should be handled by the wallet repository to ensure
            atomicity with balance updates.
        """
        # Auto-generate a unique txid
        txid = self._generate_unique_txid()

        transaction = Transaction(
            id=TransactionId(uuid4()),
            wallet_id=wallet_id,
            txid=txid,
            amount=amount,
        )

        return transaction

    def _generate_unique_txid(self) -> TxId:
        """
        Generate a unique transaction ID.

        Returns:
            Unique transaction ID
        """
        import random
        import time

        # Generate a unique txid using timestamp and random components
        timestamp = int(time.time() * 1000)  # milliseconds
        random_component = random.randint(1000, 9999)
        txid = f"tx_{timestamp}_{random_component}"

        # Ensure uniqueness by checking if it exists
        attempts = 0
        max_attempts = 10

        while self.exists_by_txid(TxId(txid)) and attempts < max_attempts:
            random_component = random.randint(1000, 9999)
            txid = f"tx_{timestamp}_{random_component}"
            attempts += 1

        if attempts >= max_attempts:
            # Fallback: use UUID-based txid
            txid = f"tx_{uuid4().hex[:16]}"

        return TxId(txid)

    def exists_by_txid(self, txid: TxId) -> bool:
        """
        Check if transaction exists by external transaction ID.

        Args:
            txid: External transaction ID to check

        Returns:
            True if transaction exists, False otherwise
        """
        return self._transaction_repository.exists_by_txid(txid)

    def get_transactions_by_wallet_id(self, wallet_id: WalletId) -> list[Transaction]:
        """
        Get all active transactions for a wallet.

        Args:
            wallet_id: Wallet ID to find transactions for

        Returns:
            List of active transaction entities
        """
        return self._transaction_repository.get_active_by_wallet_id(wallet_id)

    def get_transactions_by_wallet_ids(
        self, wallet_ids: list[WalletId]
    ) -> list[Transaction]:
        """
        Get all active transactions for multiple wallets.

        Args:
            wallet_ids: List of wallet IDs to find transactions for

        Returns:
            List of active transaction entities
        """
        return self._transaction_repository.get_active_by_wallet_ids(wallet_ids)

    def deactivate_transaction(self, txid: TxId) -> Transaction:
        """
        Deactivate a transaction.

        Args:
            txid: External transaction ID to deactivate

        Returns:
            Deactivated transaction entity

        Raises:
            TransactionNotFoundException: If transaction is not found
        """
        transaction = self.get_transaction_by_txid(txid)
        transaction.deactivate()
        return self._transaction_repository.save(transaction)

    def get_all_active_transactions(self) -> list[Transaction]:
        """
        Get all active transactions.

        Returns:
            List of active transaction entities
        """
        return self._transaction_repository.get_all_active()
