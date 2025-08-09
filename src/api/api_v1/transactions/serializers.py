"""
Transaction API serializers.

This module handles data validation and transformation between
the API layer and the application layer.
"""
# Standard library imports
from decimal import Decimal, InvalidOperation
from uuid import UUID

# Third-party imports
from rest_framework import serializers

# Local imports
from src.domain.transactions.entities import Transaction


class TransactionSerializer(serializers.Serializer):
    """
    Transaction serializer for API responses.

    Converts domain entities to JSON:API-compliant response format.
    """

    id = serializers.UUIDField()
    wallet_id = serializers.UUIDField()
    txid = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=18, decimal_places=0)
    is_active = serializers.BooleanField()
    deactivated_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def to_representation(self, instance: Transaction) -> dict:
        """
        Convert domain entity to JSON:API representation.

        Args:
            instance: Transaction domain entity

        Returns:
            Dictionary representation for API response
        """
        return {
            "type": "transactions",
            "id": str(instance.id),
            "attributes": {
                "wallet_id": str(instance.wallet_id),
                "txid": instance.txid,
                "amount": int(instance.amount),
                "is_active": instance.is_active,
                "deactivated_at": instance.deactivated_at.isoformat()
                if instance.deactivated_at
                else None,
                "created_at": instance.created_at.isoformat(),
                "updated_at": instance.updated_at.isoformat(),
            },
        }


class TransactionListFilterSerializer(serializers.Serializer):
    """
    Serializer for transaction list filters.

    Handles validation of query parameters for filtering transactions.
    """

    wallet_ids = serializers.CharField(required=False, allow_blank=True)

    def validate_wallet_ids(self, value: str) -> list:
        """
        Parse and validate comma-separated wallet IDs.

        Args:
            value: Comma-separated wallet ID string

        Returns:
            List of validated wallet ID strings

        Raises:
            serializers.ValidationError: If wallet IDs are invalid
        """
        if not value:
            return []

        wallet_ids = [
            wallet_id.strip() for wallet_id in value.split(",") if wallet_id.strip()
        ]

        # Validate UUID format for each wallet ID
        for wallet_id in wallet_ids:
            try:
                UUID(wallet_id)
            except ValueError as e:
                raise serializers.ValidationError(
                    f"Invalid wallet ID format: {wallet_id}"
                ) from e


        return wallet_ids


class CreateTransactionSerializer(serializers.Serializer):
    """
    Serializer for transaction creation requests.

    Validates input data and ensures proper format for business logic.
    """

    wallet_id = serializers.CharField(max_length=36, help_text="Wallet UUID")
    amount = serializers.CharField(
        help_text="Transaction amount (positive for credits, negative for debits)"
    )

    def validate_wallet_id(self, value: str) -> str:
        """
        Validate wallet ID field.

        Args:
            value: Wallet ID value

        Returns:
            Validated wallet ID

        Raises:
            serializers.ValidationError: If wallet ID is invalid
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Wallet ID cannot be empty")

        # Validate UUID format
        try:
            UUID(value.strip())
        except ValueError as err:
            raise serializers.ValidationError("Invalid wallet ID format") from err

        return value.strip()

    def validate_amount(self, value: str) -> str:
        """
        Validate amount field.

        Args:
            value: Amount value

        Returns:
            Validated amount

        Raises:
            serializers.ValidationError: If amount is invalid
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Amount cannot be empty")

        try:
            amount_decimal = Decimal(value.strip())
        except (InvalidOperation, ValueError) as err:
            raise serializers.ValidationError("Amount must be a valid number") from err

        if amount_decimal == 0:
            raise serializers.ValidationError("Amount cannot be zero")

        return value.strip()
