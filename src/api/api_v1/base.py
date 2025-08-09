"""
Base API ViewSet for common functionality.
"""
from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from src.domain.shared.exceptions import DomainException, WalletNotFoundException


class BaseApiViewSet(GenericViewSet):
    """
    Base API ViewSet that provides common functionality for all API endpoints.

    Features:
    - Standardized success response formatting
    - Domain exception handling
    - Request attribute extraction for JSON:API-style payloads
    - Common error response methods
    - Pagination support through GenericViewSet inheritance
    """

    def paginate_queryset(self, queryset):
        """
        Paginate a queryset if pagination is enabled.

        Args:
            queryset: The queryset to paginate

        Returns:
            Paginated queryset or None if pagination is disabled
        """
        if not hasattr(self, "paginator"):
            return None

        if self.paginator is None:
            return None

        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated response.

        Args:
            data: The paginated data

        Returns:
            Paginated response
        """
        if not hasattr(self, "paginator"):
            return Response(data)

        if self.paginator is None:
            return Response(data)

        return self.paginator.get_paginated_response(data)

    def _handle_domain_exception(self, exc: Exception) -> Response:
        """
        Handle domain exceptions and convert them to appropriate DRF responses.

        Args:
            exc: Domain exception

        Returns:
            DRF Response with appropriate error details
        """
        if isinstance(exc, WalletNotFoundException):
            raise NotFound(detail=str(exc))
        elif isinstance(exc, DomainException) or isinstance(exc, ValidationError):
            raise ValidationError(detail=str(exc))
        else:
            raise APIException(detail="An unexpected error occurred")

    def _extract_request_attributes(self, data: dict) -> dict:
        """
        Extract the 'attributes' dictionary from a JSON:API-style request.

        Args:
            data: Request data dictionary

        Returns:
            Extracted attributes or original data if not in JSON:API format
        """
        if "data" in data and "attributes" in data["data"]:
            return data["data"]["attributes"]
        return data

    def _create_success_response(
        self,
        data: Any,
        status_code: int = status.HTTP_200_OK,
        serializer_class: type[Serializer] | None = None,
    ) -> Response:
        """
        Create a standardized success response with the 'data' wrapper.

        Args:
            data: Response data
            status_code: HTTP status code
            serializer_class: Optional serializer class for data transformation

        Returns:
            DRF Response with standardized format
        """
        if serializer_class:
            if hasattr(data, "__iter__") and not isinstance(data, str | bytes):
                # Handle lists/querysets
                response_data = serializer_class(data, many=True).data
            else:
                # Handle single objects
                response_data = serializer_class(data).data
        else:
            response_data = data

        return Response({"data": response_data}, status=status_code)

    def _create_bad_request_response(
        self,
        detail: str,
        source: dict[str, str] | None = None,
        meta: dict[str, Any] | None = None,
    ) -> Response:
        """
        Create a standardized bad request error response.

        Args:
            detail: Error detail message
            source: Optional source information for the error
            meta: Optional additional metadata

        Returns:
            DRF Response with bad request error
        """
        error = {
            "status": "400",
            "title": "Bad Request",
            "detail": detail,
        }

        if source:
            error["source"] = source
        if meta:
            error["meta"] = meta

        return Response({"errors": [error]}, status=status.HTTP_400_BAD_REQUEST)

    def _create_error_response(self, errors: list[dict], status_code: int) -> Response:
        """
        Create a standardized error response.

        Args:
            errors: List of error dictionaries
            status_code: HTTP status code

        Returns:
            DRF Response with error details
        """
        return Response({"errors": errors}, status=status_code)
