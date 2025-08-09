"""
Transaction API views.

This module handles HTTP orchestration for transaction operations,
delegating business logic to the application layer.
"""
# Standard library imports
from typing import Any

# Django imports
from django.http import HttpRequest

# Third-party imports
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from src.api.api_v1.base import BaseApiViewSet
from src.api.api_v1.parsers import JSONAPIParser
from src.api.api_v1.transactions.docs import (
    CREATE_TRANSACTION_REQUEST_EXAMPLE,
    CREATE_TRANSACTION_RESPONSES,
    CREATE_TRANSACTION_SUCCESS_EXAMPLE,
    GET_TRANSACTION_RESPONSES,
    GET_TRANSACTION_SUCCESS_EXAMPLE,
    LIST_TRANSACTIONS_RESPONSES,
    ORDERING_PARAMETER,
    PAGINATION_PARAMETERS,
    TXID_PATH_PARAMETER,
    WALLET_IDS_QUERY_PARAMETER,
)
from src.api.api_v1.transactions.serializers import (
    CreateTransactionSerializer,
    TransactionListFilterSerializer,
    TransactionSerializer,
)
from src.application.transactions.commands import CreateTransactionCommand

# Local imports
from src.application.transactions.queries import (
    GetTransactionByTxidQuery,
    ListTransactionsWithDatabasePaginationQuery,
)
from src.containers import UseCaseContainer


class TransactionViewSet(BaseApiViewSet):
    """
    Transaction ViewSet for handling transaction operations.

    This ViewSet is responsible for:
    - HTTP request/response handling
    - Input validation and serialization
    - Delegating business logic to application layer use cases
    - Standardized error handling and response formatting
    """

    permission_classes = [AllowAny]
    parser_classes = [JSONParser, JSONAPIParser]

    def _validate_query_params(self, request: HttpRequest) -> dict[str, Any]:
        """
        Validate and parse query parameters.

        Args:
            request: HTTP request with query parameters

        Returns:
            Validated query parameters

        Raises:
            Response: Bad request response if validation fails
        """
        serializer = TransactionListFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return self._create_bad_request_response(
                detail="Invalid query parameters",
                source={"parameter": "query"},
                meta={"validation_errors": serializer.errors},
            )
        return serializer.validated_data

    @extend_schema(
        tags=["transactions"],
        summary="List transactions",
        description="Get a list of transactions with optional filtering by wallet IDs. Results are ordered by created_at in descending order (newest first) by default.",
        parameters=[
            WALLET_IDS_QUERY_PARAMETER,
            *PAGINATION_PARAMETERS,
            ORDERING_PARAMETER,
        ],
        responses=LIST_TRANSACTIONS_RESPONSES,
    )
    @action(detail=False, methods=["get"], url_path="list")
    def list_transactions(self, request: HttpRequest) -> Response:
        """
        List transactions with optional filtering and database-level pagination.

        Args:
            request: HTTP request with optional query parameters

        Returns:
            HTTP response with paginated list of transactions
        """
        try:
            # Validate query parameters
            validated_params = self._validate_query_params(request)
            if isinstance(validated_params, Response):
                return validated_params

            # Parse pagination parameters
            page_number = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 20))

            # Validate pagination parameters
            if page_number < 1:
                raise ValueError("Page number must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise ValueError("Page size must be between 1 and 100")

            # Parse ordering parameter
            ordering = request.query_params.get("ordering")

            # Call use case for database-level pagination and filtering
            use_case = (
                UseCaseContainer.list_transactions_with_database_pagination_use_case()
            )
            query = ListTransactionsWithDatabasePaginationQuery(
                wallet_ids_str=validated_params.get("wallet_ids"),
                is_active_str=validated_params.get("is_active"),
                page_number=page_number,
                page_size=page_size,
                ordering=ordering,
            )

            # Get paginated and filtered data from database
            result = use_case.execute(query)

            # Serialize the data
            serializer = TransactionSerializer(result["data"], many=True)

            # Build the response with JSON:API pagination format
            response_data = {
                "links": result["links"],
                "meta": result["meta"],
                "data": serializer.data,
            }

            return Response(response_data)

        except ValueError as e:
            return self._create_bad_request_response(
                detail=str(e), source={"parameter": "query"}
            )
        except Exception as e:
            return self._handle_domain_exception(e)

    @extend_schema(
        tags=["transactions"],
        summary="Create transaction",
        description="Create a new transaction for a wallet.",
        request=CreateTransactionSerializer,
        responses=CREATE_TRANSACTION_RESPONSES,
        examples=[
            CREATE_TRANSACTION_REQUEST_EXAMPLE,
            CREATE_TRANSACTION_SUCCESS_EXAMPLE,
        ],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_transaction(self, request: HttpRequest) -> Response:
        """
        Create a new transaction.

        Args:
            request: HTTP request with transaction data

        Returns:
            HTTP response with created transaction data
        """
        try:
            # Extract and validate request data
            request_data = self._extract_request_attributes(request.data)
            serializer = CreateTransactionSerializer(data=request_data)
            serializer.is_valid(raise_exception=True)

            # Execute use case
            use_case = UseCaseContainer.create_transaction_use_case()
            command = CreateTransactionCommand(
                wallet_id_str=serializer.validated_data["wallet_id"],
                amount_str=str(serializer.validated_data["amount"]),
            )
            transaction = use_case.execute(command)

            # Return standardized response
            return self._create_success_response(
                transaction,
                status_code=status.HTTP_201_CREATED,
                serializer_class=TransactionSerializer,
            )

        except ValueError as e:
            return self._create_bad_request_response(
                detail=str(e), source={"pointer": "/data/attributes"}
            )
        except Exception as e:
            import traceback

            traceback.print_exc()
            return self._handle_domain_exception(e)

    @extend_schema(
        tags=["transactions"],
        summary="Get transaction by txid",
        description="Retrieve a transaction by its external transaction ID (txid)",
        responses=GET_TRANSACTION_RESPONSES,
        parameters=[TXID_PATH_PARAMETER],
        examples=[GET_TRANSACTION_SUCCESS_EXAMPLE],
    )
    @action(detail=False, methods=["get"], url_path="by-txid/(?P<txid>[^/.]+)")
    def get_transaction_by_txid(self, request: HttpRequest, txid: str) -> Response:
        """
        Get transaction by external transaction ID (txid).

        Args:
            request: HTTP request
            txid: External transaction ID from URL

        Returns:
            HTTP response with transaction data
        """
        try:
            # Execute use case
            use_case = UseCaseContainer.get_transaction_by_txid_use_case()
            query = GetTransactionByTxidQuery(txid=txid)
            transaction = use_case.execute(query)

            # Return standardized response
            return self._create_success_response(
                transaction, serializer_class=TransactionSerializer
            )

        except ValueError as e:
            return self._create_bad_request_response(
                detail=str(e), source={"parameter": "txid"}
            )
        except Exception as e:
            return self._handle_domain_exception(e)
