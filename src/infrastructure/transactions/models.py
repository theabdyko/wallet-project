"""
Django Transaction model.
"""
from uuid import uuid4

from django.db import models
from django.utils import timezone

from src.infrastructure.wallets.models import Wallet


class Transaction(models.Model):
    """
    Django Transaction model.

    This is the infrastructure implementation of the Transaction domain entity.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    txid = models.CharField(max_length=255, unique=True, null=False, blank=False)
    amount = models.DecimalField(max_digits=18, decimal_places=0)
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"
        indexes = [
            models.Index(fields=["wallet", "is_active"]),
            models.Index(fields=["txid"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"Transaction {self.id} - {self.txid}"

    def deactivate(self) -> None:
        """
        Deactivate the transaction.

        This method sets is_active to False and deactivated_at to current time.
        """
        if self.is_active:
            self.is_active = False
            self.deactivated_at = timezone.now()
            self.save(update_fields=["is_active", "deactivated_at", "updated_at"])

    @property
    def is_deactivated(self) -> bool:
        """Check if transaction is deactivated."""
        return not self.is_active

    @property
    def is_credit(self) -> bool:
        """Check if transaction is a credit (positive amount)."""
        return self.amount > 0

    @property
    def is_debit(self) -> bool:
        """Check if transaction is a debit (negative amount)."""
        return self.amount < 0

    def get_amount_display(self) -> str:
        """Get formatted amount display."""
        return f"{self.amount:,}"
