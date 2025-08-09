"""
Django admin configuration.
"""
from django.contrib import admin

from src.infrastructure.transactions.models import Transaction
from src.infrastructure.wallets.models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """Admin configuration for Wallet model."""

    list_display = [
        "id",
        "label",
        "balance",
        "is_active",
        "deactivated_at",
        "created_at",
        "updated_at",
    ]
    list_filter = ["is_active", "created_at", "updated_at"]
    search_fields = ["id", "label"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("id", "label", "balance")}),
        ("Status", {"fields": ("is_active", "deactivated_at")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin configuration for Transaction model."""

    list_display = [
        "id",
        "wallet",
        "txid",
        "amount",
        "is_active",
        "deactivated_at",
        "created_at",
        "updated_at",
    ]
    list_filter = ["is_active", "created_at", "updated_at", "wallet"]
    search_fields = ["id", "txid", "wallet__label"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("id", "wallet", "txid", "amount")}),
        ("Status", {"fields": ("is_active", "deactivated_at")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
