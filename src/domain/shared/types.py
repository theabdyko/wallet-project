"""
Shared types for the domain layer.
"""
from decimal import Decimal
from typing import NewType
from uuid import UUID

# Type aliases for better type safety
WalletId = NewType("WalletId", UUID)
TransactionId = NewType("TransactionId", UUID)
Money = NewType("Money", Decimal)
TxId = NewType("TxId", str)

# Union types
EntityId = WalletId | TransactionId
