"""
Django Wallet model.
"""
from decimal import Decimal
from uuid import uuid4

from django.db import models
from django.utils import timezone


class Wallet(models.Model):
    """
    Django Wallet model.

    This is the infrastructure implementation of the Wallet domain entity.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    label = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=18, decimal_places=0, default=Decimal("0"))
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wallets"
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"Wallet {self.id} - {self.label}"

    def deactivate(self) -> None:
        """
        Deactivate the wallet.

        This method sets is_active to False and deactivated_at to current time.
        """
        if self.is_active:
            self.is_active = False
            self.deactivated_at = timezone.now()
            self.save(update_fields=["is_active", "deactivated_at", "updated_at"])

    @property
    def is_deactivated(self) -> bool:
        """Check if wallet is deactivated."""
        return not self.is_active

    def get_balance_display(self) -> str:
        """Get formatted balance display."""
        return f"{self.balance:,}"
