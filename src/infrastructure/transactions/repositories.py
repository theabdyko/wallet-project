"""
Django implementation of TransactionRepository.
"""

from django.db import transaction
from django.utils import timezone

from src.domain.shared.types import TransactionId, TxId, WalletId
from src.domain.transactions.entities import Transaction
from src.domain.transactions.repositories import TransactionRepository
from src.infrastructure.transactions.models import Transaction as TransactionModel
from src.infrastructure.wallets.models import Wallet as WalletModel


class DjangoTransactionRepository(TransactionRepository):
    """
    Django implementation of TransactionRepository.

    This class implements the TransactionRepository interface using Django ORM
    with atomic transactions and database locking for concurrency safety.
    """

    def get_by_id(self, transaction_id: TransactionId) -> Transaction | None:
        """
        Get transaction by ID.

        Args:
            transaction_id: Transaction ID to find

        Returns:
            Transaction entity if found, None otherwise
        """
        try:
            transaction_model = TransactionModel.objects.get(id=transaction_id)
            return self._to_domain_entity(transaction_model)
        except TransactionModel.DoesNotExist:
            return None

    def get_by_txid(self, txid: TxId) -> Transaction | None:
        """
        Get transaction by external transaction ID.

        Args:
            txid: External transaction ID to find

        Returns:
            Transaction entity if found, None otherwise
        """
        try:
            transaction_model = TransactionModel.objects.get(txid=txid)
            return self._to_domain_entity(transaction_model)
        except TransactionModel.DoesNotExist:
            return None

    def get_active_by_txid(self, txid: TxId) -> Transaction | None:
        """
        Get active transaction by external transaction ID.

        Args:
            txid: External transaction ID to find

        Returns:
            Active transaction entity if found, None otherwise
        """
        try:
            transaction_model = TransactionModel.objects.filter(is_active=True).get(
                txid=txid
            )
            return self._to_domain_entity(transaction_model)
        except TransactionModel.DoesNotExist:
            return None

    def save(self, transaction: Transaction) -> Transaction:
        """
        Save transaction to database.

        Args:
            transaction: Transaction entity to save

        Returns:
            Saved transaction entity
        """
        transaction_model, created = TransactionModel.objects.update_or_create(
            id=transaction.id,
            defaults={
                "wallet_id": transaction.wallet_id,
                "txid": transaction.txid,
                "amount": transaction.amount,
                "is_active": transaction.is_active,
                "deactivated_at": transaction.deactivated_at,
            },
        )

        return self._to_domain_entity(transaction_model)

    def get_by_wallet_ids(self, wallet_ids: list[WalletId]) -> list[Transaction]:
        """
        Get all transactions for multiple wallets.

        Args:
            wallet_ids: List of wallet IDs to find transactions for

        Returns:
            List of transaction entities
        """
        if not wallet_ids:
            return []

        transaction_models = TransactionModel.objects.filter(
            wallet_id__in=wallet_ids
        ).order_by("created_at")
        return [self._to_domain_entity(tx_model) for tx_model in transaction_models]

    def get_by_wallet_id(self, wallet_id: WalletId) -> list[Transaction]:
        """
        Get all transactions for a wallet.

        Args:
            wallet_id: Wallet ID to find transactions for

        Returns:
            List of transaction entities
        """
        transaction_models = TransactionModel.objects.filter(
            wallet_id=wallet_id
        ).order_by("created_at")
        return [self._to_domain_entity(tx_model) for tx_model in transaction_models]

    def get_active_by_wallet_id(self, wallet_id: WalletId) -> list[Transaction]:
        """
        Get all active transactions for a wallet.

        Args:
            wallet_id: Wallet ID to find active transactions for

        Returns:
            List of active transaction entities
        """
        transaction_models = TransactionModel.objects.filter(
            wallet_id=wallet_id, is_active=True
        ).order_by("created_at")
        return [self._to_domain_entity(tx_model) for tx_model in transaction_models]

    def get_active_by_wallet_ids(self, wallet_ids: list[WalletId]) -> list[Transaction]:
        """
        Get all active transactions for multiple wallets.

        Args:
            wallet_ids: List of wallet IDs to find active transactions for

        Returns:
            List of active transaction entities
        """
        if not wallet_ids:
            return []

        transaction_models = TransactionModel.objects.filter(
            wallet_id__in=wallet_ids, is_active=True
        ).order_by("created_at")
        return [self._to_domain_entity(tx_model) for tx_model in transaction_models]

    def filter_transactions(
        self, is_active: bool = None, wallet_ids: list[WalletId] = None
    ) -> list[Transaction]:
        """
        Filter transactions with optional parameters.

        Args:
            is_active: Optional boolean filter for active status
            wallet_ids: Optional list of wallet IDs to filter by

        Returns:
            List of filtered transaction entities
        """
        queryset = self.get_filtered_queryset(is_active, wallet_ids)
        return [self._to_domain_entity(tx_model) for tx_model in queryset]

    def get_filtered_queryset(
        self,
        is_active: bool = None,
        wallet_ids: list[WalletId] = None,
        ordering: str | None = None,
    ):
        """
        Get filtered queryset for pagination with ordering.

        Args:
            is_active: Optional boolean filter for active status
            wallet_ids: Optional list of wallet IDs to filter by
            ordering: Optional ordering string (e.g., 'created_at', '-created_at', 'amount', '-amount')

        Returns:
            Django QuerySet for pagination with ordering
        """
        queryset = TransactionModel.objects.all()

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        if wallet_ids:
            queryset = queryset.filter(wallet_id__in=wallet_ids)

        # Apply ordering
        if ordering:
            # Validate ordering field to prevent SQL injection
            allowed_fields = {"created_at", "updated_at", "amount", "txid"}
            field_name = ordering.lstrip("-")
            if field_name in allowed_fields:
                queryset = queryset.order_by(ordering)
            else:
                # Fallback to default ordering if invalid field
                queryset = queryset.order_by("-created_at")
        else:
            # Default ordering: created_at in descending order (newest first)
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_paginated_and_filtered_transactions(
        self,
        is_active: bool = None,
        wallet_ids: list[WalletId] = None,
        page_number: int = 1,
        page_size: int = 20,
        ordering: str | None = None,
    ):
        """
        Get paginated and filtered transactions with database-level pagination.

        This method implements efficient database-level pagination and filtering
        to avoid loading unnecessary data into memory.

        Args:
            is_active: Optional boolean filter for active status (None = both active and inactive)
            wallet_ids: Optional list of wallet IDs to filter by
            page_number: Page number (1-based)
            page_size: Number of items per page
            ordering: Optional ordering string (e.g., 'created_at', '-created_at', 'amount', '-amount')

        Returns:
            Dictionary containing:
            - 'data': List of transaction entities for the current page
            - 'meta': Pagination metadata (count, page, pages, page_size)
            - 'links': Pagination links (first, last, prev, next)
        """
        from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

        # Build the base queryset with filters and ordering
        queryset = self.get_filtered_queryset(is_active, wallet_ids, ordering)

        # Get total count for pagination metadata
        total_count = queryset.count()

        # Create paginator
        paginator = Paginator(queryset, page_size)

        # Get the requested page
        try:
            page = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            # If page is out of range, deliver last page of results
            page = paginator.page(paginator.num_pages)
            page_number = paginator.num_pages

        # Convert page objects to domain entities
        transaction_entities = [
            self._to_domain_entity(tx_model) for tx_model in page.object_list
        ]

        # Build pagination metadata
        meta = {
            "count": total_count,
            "page": page_number,
            "pages": paginator.num_pages,
            "page_size": page_size,
        }

        # Build pagination links (basic format, will be enhanced by the view)
        links = {
            "first": f"?page=1&page_size={page_size}",
            "last": f"?page={paginator.num_pages}&page_size={page_size}",
            "prev": None,
            "next": None,
        }

        if page.has_previous():
            links["prev"] = f"?page={page.previous_page_number()}&page_size={page_size}"

        if page.has_next():
            links["next"] = f"?page={page.next_page_number()}&page_size={page_size}"

        # Add ordering to links if provided
        if ordering:
            for key in links:
                if links[key]:
                    links[key] += f"&ordering={ordering}"

        return {"data": transaction_entities, "meta": meta, "links": links}

    def exists_by_txid(self, txid: TxId) -> bool:
        """
        Check if transaction exists by external transaction ID.

        Args:
            txid: External transaction ID to check

        Returns:
            True if transaction exists, False otherwise
        """
        return TransactionModel.objects.filter(txid=txid).exists()

    def save_with_wallet_balance_update(self, transaction: Transaction) -> Transaction:
        """
        Save transaction and update wallet balance atomically with locking.

        Args:
            transaction: Transaction entity to save

        Returns:
            Saved transaction entity
        """
        with transaction.atomic():
            # Lock the wallet for update to ensure concurrency safety
            wallet_model = WalletModel.objects.select_for_update().get(
                id=transaction.wallet_id
            )

            # Save the transaction
            transaction_model, created = TransactionModel.objects.update_or_create(
                id=transaction.id,
                defaults={
                    "wallet_id": transaction.wallet_id,
                    "txid": transaction.txid,
                    "amount": transaction.amount,
                    "is_active": transaction.is_active,
                    "deactivated_at": transaction.deactivated_at,
                },
            )

            # Update wallet balance based on transaction
            if transaction.is_active:
                # Add transaction amount to wallet balance
                wallet_model.balance += transaction.amount
            else:
                # Subtract transaction amount from wallet balance (deactivation)
                wallet_model.balance -= transaction.amount

            wallet_model.save(update_fields=["balance", "updated_at"])

            return self._to_domain_entity(transaction_model)

    def deactivate_transactions_for_wallet(
        self, wallet_id: WalletId
    ) -> list[Transaction]:
        """
        Deactivate all active transactions for a wallet atomically.

        Args:
            wallet_id: Wallet ID to deactivate transactions for

        Returns:
            List of deactivated transaction entities
        """
        with transaction.atomic():
            # Lock the wallet for update
            wallet_model = WalletModel.objects.select_for_update().get(id=wallet_id)

            # Get all active transactions for the wallet
            transaction_models = TransactionModel.objects.filter(
                wallet_id=wallet_id, is_active=True
            ).select_for_update()

            deactivated_transactions = []
            total_deactivated_amount = 0

            # Deactivate each transaction
            for tx_model in transaction_models:
                tx_model.is_active = False
                tx_model.deactivated_at = timezone.now()
                tx_model.save(
                    update_fields=["is_active", "deactivated_at", "updated_at"]
                )

                # Subtract the transaction amount from wallet balance
                total_deactivated_amount += tx_model.amount
                deactivated_transactions.append(self._to_domain_entity(tx_model))

            # Update wallet balance
            wallet_model.balance -= total_deactivated_amount
            wallet_model.save(update_fields=["balance", "updated_at"])

            return deactivated_transactions

    def get_all_active(self) -> list[Transaction]:
        """
        Get all active transactions.

        Returns:
            List of active transaction entities
        """
        transaction_models = TransactionModel.objects.filter(is_active=True).order_by(
            "created_at"
        )
        return [self._to_domain_entity(tx_model) for tx_model in transaction_models]

    def _to_domain_entity(self, transaction_model: TransactionModel) -> Transaction:
        """
        Convert Django model to domain entity.

        Args:
            transaction_model: Django Transaction model

        Returns:
            Transaction domain entity
        """
        return Transaction(
            id=TransactionId(transaction_model.id),
            wallet_id=WalletId(transaction_model.wallet_id),
            txid=TxId(transaction_model.txid),
            amount=transaction_model.amount,
            is_active=transaction_model.is_active,
            deactivated_at=transaction_model.deactivated_at,
            created_at=transaction_model.created_at,
            updated_at=transaction_model.updated_at,
        )
