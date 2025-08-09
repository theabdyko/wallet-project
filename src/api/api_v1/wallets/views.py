"""
Wallet API views.
"""
from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import UnsupportedMediaType, ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from src.api.api_v1.base import BaseApiViewSet
from src.api.api_v1.parsers import JSONAPIParser
from src.api.api_v1.wallets.docs import (
    CREATE_WALLET_REQUEST_EXAMPLE,
    CREATE_WALLET_RESPONSES,
    CREATE_WALLET_SUCCESS_EXAMPLE,
    DEACTIVATE_WALLET_RESPONSES,
    DEACTIVATE_WALLET_SUCCESS_EXAMPLE,
    IS_ACTIVE_QUERY_PARAMETER,
    LIST_WALLETS_RESPONSES,
    ORDERING_PARAMETER,
    PAGINATION_PARAMETERS,
    UPDATE_WALLET_LABEL_REQUEST_EXAMPLE,
    UPDATE_WALLET_LABEL_RESPONSES,
    UPDATE_WALLET_LABEL_SUCCESS_EXAMPLE,
    WALLET_IDS_QUERY_PARAMETER,
)
from src.api.api_v1.wallets.serializers import (
    CreateWalletSerializer,
    UpdateWalletLabelSerializer,
    WalletListFilterSerializer,
    WalletSerializer,
)
from src.application.wallets.commands import (
    CreateWalletCommand,
    DeactivateWalletCommand,
    UpdateWalletLabelCommand,
)
from src.application.wallets.queries import ListWalletsWithDatabasePaginationQuery
from src.containers import UseCaseContainer


class WalletViewSet(BaseApiViewSet):
    """
    Wallet ViewSet for handling wallet operations.
    """

    permission_classes = [AllowAny]
    parser_classes = [JSONParser, JSONAPIParser]

    @extend_schema(
        tags=["wallets"],
        summary="Create wallet",
        description="Create a new wallet with a default balance of 0.",
        request=CreateWalletSerializer,
        responses=CREATE_WALLET_RESPONSES,
        examples=[
            CREATE_WALLET_REQUEST_EXAMPLE,
            CREATE_WALLET_SUCCESS_EXAMPLE,
        ],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_wallet(self, request: HttpRequest) -> Response:
        """
        Create a new wallet.

        Args:
            request: HTTP request with wallet data

        Returns:
            HTTP response with created wallet data
        """
        try:
            # Extract data from request format
            request_data = self._extract_request_attributes(request.data)

            # Validate request data
            serializer = CreateWalletSerializer(data=request_data)
            serializer.is_valid(raise_exception=True)

            # Call use case
            use_case = UseCaseContainer.create_wallet_use_case()
            command = CreateWalletCommand(label=serializer.validated_data["label"])
            wallet = use_case.execute(command)

            # Return standardized response
            return self._create_success_response(
                wallet,
                status_code=status.HTTP_201_CREATED,
                serializer_class=WalletSerializer,
            )

        except ValueError as e:
            raise ValidationError(detail=str(e)) from e
        except Exception as e:
            self._handle_domain_exception(e)

    @extend_schema(
        tags=["wallets"],
        summary="List wallets",
        description="Get a list of wallets with optional filtering by wallet IDs and active status. Results are ordered by balance in descending order (highest balance first) by default.",
        parameters=[
            WALLET_IDS_QUERY_PARAMETER,
            IS_ACTIVE_QUERY_PARAMETER,
            *PAGINATION_PARAMETERS,
            ORDERING_PARAMETER,
        ],
        responses=LIST_WALLETS_RESPONSES,
    )
    @action(detail=False, methods=["get"], url_path="list")
    def list_wallets(self, request: HttpRequest) -> Response:
        """
        List wallets with optional filtering and database-level pagination.

        Args:
            request: HTTP request with optional query parameters

        Returns:
            HTTP response with paginated list of wallets
        """
        try:
            # Validate query parameters
            filter_serializer = WalletListFilterSerializer(data=request.query_params)
            filter_serializer.is_valid(raise_exception=True)

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
            use_case = UseCaseContainer.list_wallets_with_database_pagination_use_case()

            query = ListWalletsWithDatabasePaginationQuery(
                wallet_ids_str=filter_serializer.validated_data.get("wallet_ids"),
                is_active_str=filter_serializer.validated_data.get("is_active"),
                page_number=page_number,
                page_size=page_size,
                ordering=ordering,
            )

            # Get paginated and filtered data from database
            result = use_case.execute(query)

            # Serialize the data
            serializer = WalletSerializer(result["data"], many=True)

            # Build the response with JSON:API pagination format
            response_data = {
                "links": result["links"],
                "meta": result["meta"],
                "data": serializer.data,
            }

            return Response(response_data)

        except (ValueError, UnsupportedMediaType) as e:
            raise ValidationError(detail=str(e)) from e
        except Exception as e:
            self._handle_domain_exception(e)

    @extend_schema(
        tags=["wallets"],
        summary="Update wallet label",
        description="Update the label of an existing wallet. Only the label field can be updated.",
        request=UpdateWalletLabelSerializer,
        responses=UPDATE_WALLET_LABEL_RESPONSES,
        examples=[
            UPDATE_WALLET_LABEL_REQUEST_EXAMPLE,
            UPDATE_WALLET_LABEL_SUCCESS_EXAMPLE,
        ],
    )
    @action(detail=True, methods=["patch"], url_path="update-label")
    def update_wallet_label(self, request: HttpRequest, pk: str = None) -> Response:
        """
        Update wallet label.

        Args:
            request: HTTP request
            pk: Wallet ID from URL

        Returns:
            HTTP response with updated wallet data
        """
        try:
            # Extract data from request format
            request_data = self._extract_request_attributes(request.data)

            # Validate request data
            serializer = UpdateWalletLabelSerializer(data=request_data)
            serializer.is_valid(raise_exception=True)

            # Call use case
            use_case = UseCaseContainer.update_wallet_label_use_case()
            command = UpdateWalletLabelCommand(
                wallet_id_str=pk, new_label=serializer.validated_data["label"]
            )
            wallet = use_case.execute(command)

            # Return standardized response
            return self._create_success_response(
                wallet, serializer_class=WalletSerializer
            )

        except ValueError as e:
            raise ValidationError(detail=str(e)) from e
        except Exception as e:
            self._handle_domain_exception(e)

    @extend_schema(
        tags=["wallets"],
        summary="Deactivate wallet",
        description="Deactivate a wallet and all its related transactions. This operation is atomic and will soft-delete both the wallet and all its transactions.",
        responses=DEACTIVATE_WALLET_RESPONSES,
        examples=[DEACTIVATE_WALLET_SUCCESS_EXAMPLE],
    )
    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate_wallet(self, request: HttpRequest, pk: str = None) -> Response:
        """
        Deactivate wallet and all its transactions.

        Args:
            request: HTTP request
            pk: Wallet ID from URL

        Returns:
            HTTP response with deactivated wallet data
        """
        try:
            # Call use case
            use_case = UseCaseContainer.deactivate_wallet_use_case()
            command = DeactivateWalletCommand(wallet_id_str=pk)
            wallet = use_case.execute(command)

            # Return standardized response
            return self._create_success_response(
                wallet, serializer_class=WalletSerializer
            )

        except ValueError as e:
            raise ValidationError(detail=str(e)) from e
        except Exception as e:
            self._handle_domain_exception(e)
