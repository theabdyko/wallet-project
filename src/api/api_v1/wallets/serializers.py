"""
Wallet API serializers.
"""
from uuid import UUID

from rest_framework import serializers

from src.domain.wallets.entities import Wallet


class WalletSerializer(serializers.Serializer):
    """
    Wallet serializer for API responses.
    """

    id = serializers.UUIDField()
    label = serializers.CharField(max_length=255)
    balance = serializers.IntegerField()
    is_active = serializers.BooleanField()
    deactivated_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def to_representation(self, instance: Wallet) -> dict:
        """
        Convert domain entity to API representation.

        Args:
            instance: Wallet domain entity

        Returns:
            Dictionary representation for API response
        """
        return {
            "type": "wallets",
            "id": str(instance.id),
            "attributes": {
                "label": instance.label,
                "balance": int(instance.balance),
                "is_active": instance.is_active,
                "deactivated_at": instance.deactivated_at.isoformat()
                if instance.deactivated_at
                else None,
                "created_at": instance.created_at.isoformat(),
                "updated_at": instance.updated_at.isoformat(),
            },
        }


class CreateWalletSerializer(serializers.Serializer):
    """
    Serializer for creating wallet.
    Only accepts the fields needed for wallet creation.
    """

    label = serializers.CharField(max_length=255, min_length=1)

    def validate_label(self, value: str) -> str:
        """
        Validate label field.

        Args:
            value: Label value

        Returns:
            Validated label

        Raises:
            serializers.ValidationError: If label is invalid
        """
        if not value.strip():
            raise serializers.ValidationError("Label cannot be empty")
        return value.strip()


class UpdateWalletLabelSerializer(serializers.Serializer):
    """
    Serializer for updating wallet label.
    """

    label = serializers.CharField(max_length=255, min_length=1)

    def validate_label(self, value: str) -> str:
        """
        Validate label field.

        Args:
            value: Label value

        Returns:
            Validated label

        Raises:
            serializers.ValidationError: If label is invalid
        """
        if not value.strip():
            raise serializers.ValidationError("Label cannot be empty")
        return value.strip()


class WalletListFilterSerializer(serializers.Serializer):
    """
    Serializer for wallet list filters.
    """

    wallet_ids = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.CharField(required=False, allow_blank=True)

    def validate_wallet_ids(self, value: str) -> list:
        """
        Parse comma-separated wallet IDs.

        Args:
            value: Comma-separated wallet ID string

        Returns:
            List of wallet ID strings

        Raises:
            serializers.ValidationError: If wallet IDs are invalid
        """
        if not value:
            return []

        wallet_ids = [
            wallet_id.strip() for wallet_id in value.split(",") if wallet_id.strip()
        ]

        # Validate UUID format
        for wallet_id in wallet_ids:
            try:
                UUID(wallet_id)
            except ValueError as err:
                raise serializers.ValidationError(
                    f"Invalid wallet ID format: {wallet_id}"
                ) from err

        return wallet_ids
