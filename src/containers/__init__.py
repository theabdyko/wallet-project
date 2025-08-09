"""
Containers module for dependency injection containers.

This module provides organized dependency injection containers for the application.
"""

from .repositories import RepositoryContainer
from .services import ServiceContainer
from .use_cases import UseCaseContainer

# Legacy alias for backward compatibility
Container = UseCaseContainer

__all__ = [
    "RepositoryContainer",
    "ServiceContainer",
    "UseCaseContainer",
    "Container",  # Legacy alias
]
