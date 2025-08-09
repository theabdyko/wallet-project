"""
Shared domain exceptions.
"""
from typing import Any


class DomainException(Exception):
    """Base domain exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class WalletNotFoundException(DomainException):
    """Raised when a wallet is not found."""

    pass


class TransactionNotFoundException(DomainException):
    """Raised when a transaction is not found."""

    pass


class InsufficientBalanceException(DomainException):
    """Raised when wallet has insufficient balance for a transaction."""

    pass


class InvalidTransactionException(DomainException):
    """Raised when a transaction is invalid."""

    pass


class WalletAlreadyDeactivatedException(DomainException):
    """Raised when trying to deactivate an already deactivated wallet."""

    pass


class TransactionAlreadyDeactivatedException(DomainException):
    """Raised when trying to deactivate an already deactivated transaction."""

    pass
