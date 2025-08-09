"""
Django implementation of WalletRepository.
"""
from django.db.models import QuerySet

from src.domain.shared.types import WalletId
from src.domain.transactions.entities import Transaction
from src.domain.wallets.entities import Wallet
from src.domain.wallets.repositories import WalletRepository
from src.infrastructure.wallets.models import Wallet as WalletModel


class DjangoWalletRepository(WalletRepository):
    """
    Django implementation of WalletRepository.

    This class implements the WalletRepository interface using Django ORM.
    """

    def get_by_id(self, wallet_id: WalletId) -> Wallet | None:
        """
        Get wallet by ID.

        Args:
            wallet_id: Wallet ID to find

        Returns:
            Wallet entity if found, None otherwise
        """
        try:
            wallet_model = WalletModel.objects.get(id=wallet_id)
            return self._to_domain_entity(wallet_model)
        except WalletModel.DoesNotExist:
            return None

    def get_active_by_id(self, wallet_id: WalletId) -> Wallet | None:
        """
        Get active wallet by ID.

        Args:
            wallet_id: Wallet ID to find

        Returns:
            Active wallet entity if found, None otherwise
        """
        try:
            wallet_model = WalletModel.objects.filter(is_active=True).get(id=wallet_id)
            return self._to_domain_entity(wallet_model)
        except WalletModel.DoesNotExist:
            return None

    def save(self, wallet: Wallet) -> Wallet:
        """
        Save wallet entity.

        Args:
            wallet: Wallet entity to save

        Returns:
            Saved wallet entity
        """
        wallet_model, created = WalletModel.objects.update_or_create(
            id=wallet.id,
            defaults={
                "label": wallet.label,
                "balance": wallet.balance,
                "is_active": wallet.is_active,
                "deactivated_at": wallet.deactivated_at,
            },
        )

        return self._to_domain_entity(wallet_model)

    def get_all_active(self) -> list[Wallet]:
        """
        Get all active wallets.

        Returns:
            List of active wallet entities
        """
        wallet_models = WalletModel.objects.filter(is_active=True).order_by(
            "created_at"
        )
        return [self._to_domain_entity(wallet_model) for wallet_model in wallet_models]

    def get_all_inactive(self) -> list[Wallet]:
        """
        Get all inactive wallets.

        Returns:
            List of inactive wallet entities
        """
        wallet_models = WalletModel.objects.filter(is_active=False).order_by(
            "created_at"
        )
        return [self._to_domain_entity(wallet_model) for wallet_model in wallet_models]

    def get_all(self) -> list[Wallet]:
        """
        Get all wallets.

        Returns:
            List of all wallet entities
        """
        wallet_models = WalletModel.objects.all().order_by("created_at")
        return [self._to_domain_entity(wallet_model) for wallet_model in wallet_models]

    def get_by_ids(self, wallet_ids: list[WalletId]) -> list[Wallet]:
        """
        Get wallets by IDs.

        Args:
            wallet_ids: List of wallet IDs to find

        Returns:
            List of wallet entities
        """
        wallet_models = WalletModel.objects.filter(id__in=wallet_ids)
        return [self._to_domain_entity(wallet_model) for wallet_model in wallet_models]

    def filter_wallets(
        self,
        is_active: bool | None = None,
        wallet_ids: list[WalletId] | None = None,
    ) -> list[Wallet]:
        """
        Filter wallets with multiple optional parameters.

        Args:
            is_active: Optional boolean filter for active status (None = both active and inactive)
            wallet_ids: Optional list of wallet IDs to filter by

        Returns:
            List of filtered wallet entities
        """
        queryset = self._build_filter_queryset(is_active, wallet_ids)
        return [self._to_domain_entity(wallet_model) for wallet_model in queryset]

    def _build_filter_queryset(
        self,
        is_active: bool | None = None,
        wallet_ids: list[WalletId] | None = None,
        ordering: str | None = None,
    ) -> QuerySet:
        """
        Build a Django QuerySet with the specified filters and ordering.

        Args:
            is_active: Optional boolean filter for active status
            wallet_ids: Optional list of wallet IDs to filter by
            ordering: Optional ordering string (e.g., 'balance', '-balance', 'created_at', '-created_at')

        Returns:
            Django QuerySet with applied filters and ordering
        """
        queryset = WalletModel.objects.all()

        # Apply is_active filter if provided
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        # Apply wallet_ids filter if provided
        if wallet_ids:
            queryset = queryset.filter(id__in=wallet_ids)

        # Apply ordering
        if ordering:
            # Validate ordering field to prevent SQL injection
            allowed_fields = {"balance", "created_at", "updated_at", "label"}
            field_name = ordering.lstrip("-")
            if field_name in allowed_fields:
                queryset = queryset.order_by(ordering)
            else:
                # Fallback to default ordering if invalid field
                queryset = queryset.order_by("-balance")
        else:
            # Default ordering: balance in descending order (highest first)
            queryset = queryset.order_by("-balance")

        return queryset

    def get_filtered_queryset(
        self,
        is_active: bool | None = None,
        wallet_ids: list[WalletId] | None = None,
        ordering: str | None = None,
    ) -> QuerySet:
        """
        Get a Django QuerySet with the specified filters for pagination.

        Args:
            is_active: Optional boolean filter for active status (None = both active and inactive)
            wallet_ids: Optional list of wallet IDs to filter by
            ordering: Optional ordering string (e.g., 'balance', '-balance', 'created_at', '-created_at')

        Returns:
            Django QuerySet with applied filters and ordering
        """
        return self._build_filter_queryset(is_active, wallet_ids, ordering)

    def get_paginated_and_filtered_wallets(
        self,
        is_active: bool | None = None,
        wallet_ids: list[WalletId] | None = None,
        page_number: int = 1,
        page_size: int = 20,
        ordering: str | None = None,
    ):
        """
        Get paginated and filtered wallets with database-level pagination.

        This method implements efficient database-level pagination and filtering
        to avoid loading unnecessary data into memory.

        Args:
            is_active: Optional boolean filter for active status (None = both active and inactive)
            wallet_ids: Optional list of wallet IDs to filter by
            page_number: Page number (1-based)
            page_size: Number of items per page
            ordering: Optional ordering string (e.g., 'balance', '-balance', 'created_at', '-created_at')

        Returns:
            Dictionary containing:
            - 'data': List of wallet entities for the current page
            - 'meta': Pagination metadata (count, page, pages, page_size)
            - 'links': Pagination links (first, last, prev, next)
        """
        from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

        # Build the base queryset with filters and ordering
        queryset = self._build_filter_queryset(is_active, wallet_ids, ordering)

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
        wallet_entities = [
            self._to_domain_entity(wallet_model) for wallet_model in page.object_list
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

        return {"data": wallet_entities, "meta": meta, "links": links}

    def get_filter_queryset(
        self,
        is_active: bool | None = None,
        wallet_ids: list[WalletId] | None = None,
    ) -> QuerySet:
        """
        Get a Django QuerySet with the specified filters for additional operations.

        Args:
            is_active: Optional boolean filter for active status (None = both active and inactive)
            wallet_ids: Optional list of wallet IDs to filter by

        Returns:
            Django QuerySet with applied filters
        """
        return self._build_filter_queryset(is_active, wallet_ids)

    def update_balance_with_transaction(
        self, wallet: Wallet, transaction: Transaction
    ) -> Wallet:
        """
        Update wallet balance atomically with transaction creation.

        Args:
            wallet: Wallet entity with updated balance
            transaction: Transaction entity to save

        Returns:
            Updated wallet entity

        Note:
            This method ensures atomicity between wallet balance update
            and transaction creation using Django's transaction.atomic().
            Balance validation happens within the atomic transaction to prevent race conditions.
        """
        from decimal import Decimal

        from django.db import transaction as django_transaction

        from src.infrastructure.transactions.models import (
            Transaction as TransactionModel,
        )

        with django_transaction.atomic():
            # Lock the wallet for update to ensure concurrency safety
            wallet_model = WalletModel.objects.select_for_update().get(id=wallet.id)

            # Calculate new balance within the atomic transaction
            current_balance = wallet_model.balance
            new_balance = current_balance + transaction.amount

            # Validate balance cannot be negative
            if new_balance < Decimal("0"):
                raise ValueError(
                    f"Transaction would result in negative balance. "
                    f"Current: {current_balance}, Transaction: {transaction.amount}, "
                    f"New Balance: {new_balance}"
                )

            # Update wallet balance
            wallet_model.balance = new_balance
            wallet_model.updated_at = wallet.updated_at
            wallet_model.save(update_fields=["balance", "updated_at"])

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

            # Return the updated wallet entity
            return self._to_domain_entity(wallet_model)

    def exists(self, wallet_id: WalletId) -> bool:
        """
        Check if wallet exists.

        Args:
            wallet_id: Wallet ID to check

        Returns:
            True if wallet exists, False otherwise
        """
        return WalletModel.objects.filter(id=wallet_id).exists()

    def _to_domain_entity(self, wallet_model: WalletModel) -> Wallet:
        """
        Convert Django model to domain entity.

        Args:
            wallet_model: Django Wallet model

        Returns:
            Wallet domain entity
        """
        return Wallet(
            id=WalletId(wallet_model.id),
            label=wallet_model.label,
            balance=wallet_model.balance,
            is_active=wallet_model.is_active,
            deactivated_at=wallet_model.deactivated_at,
            created_at=wallet_model.created_at,
            updated_at=wallet_model.updated_at,
        )
