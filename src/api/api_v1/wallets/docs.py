"""
OpenAPI schemas and examples for wallet endpoints.
"""
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse

# Shared Response Schemas
WALLET_ATTRIBUTES_SCHEMA = {
    "type": "object",
    "properties": {
        "label": {"type": "string"},
        "balance": {"type": "integer"},
        "is_active": {"type": "boolean"},
        "deactivated_at": {"type": "string", "format": "date-time", "nullable": True},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
    },
}

WALLET_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "example": "wallets"},
        "id": {"type": "string", "format": "uuid"},
        "attributes": WALLET_ATTRIBUTES_SCHEMA,
    },
}

WALLET_LIST_RESPONSE_SCHEMA = {"type": "array", "items": WALLET_RESPONSE_SCHEMA}

# Shared Request Examples
CREATE_WALLET_REQUEST_EXAMPLE = OpenApiExample(
    "Request Example",
    value={"data": {"type": "wallets", "attributes": {"label": "My New Wallet"}}},
    request_only=True,
)

UPDATE_WALLET_LABEL_REQUEST_EXAMPLE = OpenApiExample(
    "Request Example",
    value={
        "data": {"type": "wallets", "attributes": {"label": "Updated Wallet Label"}}
    },
    request_only=True,
)

# Shared Response Examples
CREATE_WALLET_SUCCESS_EXAMPLE = OpenApiExample(
    "Success Response",
    value={
        "data": {
            "type": "wallets",
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "attributes": {
                "label": "My New Wallet",
                "balance": 0,
                "is_active": True,
                "deactivated_at": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        }
    },
    response_only=True,
    status_codes=["201"],
)

UPDATE_WALLET_LABEL_SUCCESS_EXAMPLE = OpenApiExample(
    "Success Response",
    value={
        "data": {
            "type": "wallets",
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "attributes": {
                "label": "Updated Wallet Label",
                "balance": 1000,
                "is_active": True,
                "deactivated_at": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
            },
        }
    },
    response_only=True,
    status_codes=["200"],
)

DEACTIVATE_WALLET_SUCCESS_EXAMPLE = OpenApiExample(
    "Success Response",
    value={
        "data": {
            "type": "wallets",
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "attributes": {
                "label": "My Wallet",
                "balance": 0,
                "is_active": False,
                "deactivated_at": "2024-01-01T12:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
            },
        }
    },
    response_only=True,
    status_codes=["200"],
)

# Pagination Parameters
PAGINATION_PARAMETERS = [
    OpenApiParameter(
        name="page",
        location=OpenApiParameter.QUERY,
        description="Page number, starting from 1",
        required=False,
        type=int,
        examples=[
            OpenApiExample("First page", value=1),
            OpenApiExample("Second page", value=2),
        ],
    ),
    OpenApiParameter(
        name="page_size",
        location=OpenApiParameter.QUERY,
        description="Number of results per page",
        required=False,
        type=int,
        examples=[
            OpenApiExample("10 items per page", value=10),
            OpenApiExample("50 items per page", value=50),
        ],
    ),
]

# Ordering Parameter
ORDERING_PARAMETER = OpenApiParameter(
    name="ordering",
    location=OpenApiParameter.QUERY,
    description='Field to sort by. Prefix with "-" for descending order. Default: wallets sorted by balance in descending order.',
    required=False,
    type=str,
    examples=[
        OpenApiExample("Balance ascending", value="balance"),
        OpenApiExample("Balance descending", value="-balance"),
        OpenApiExample("Created date ascending", value="created_at"),
        OpenApiExample("Created date descending", value="-created_at"),
        OpenApiExample("Label ascending", value="label"),
        OpenApiExample("Label descending", value="-label"),
    ],
)

# Pagination Response Schema
PAGINATION_LINKS_SCHEMA = {
    "type": "object",
    "properties": {
        "first": {
            "type": "string",
            "format": "uri",
            "description": "Link to first page",
        },
        "last": {
            "type": ["string", "null"],
            "format": "uri",
            "description": "Link to last page",
        },
        "prev": {
            "type": ["string", "null"],
            "format": "uri",
            "description": "Link to previous page",
        },
        "next": {
            "type": ["string", "null"],
            "format": "uri",
            "description": "Link to next page",
        },
    },
}

PAGINATION_META_SCHEMA = {
    "type": "object",
    "properties": {
        "count": {"type": "integer", "description": "Total number of items"},
        "page": {"type": "integer", "description": "Current page number"},
        "pages": {"type": "integer", "description": "Total number of pages"},
        "page_size": {"type": "integer", "description": "Number of items per page"},
    },
}

# Updated List Response Schema with Pagination
LIST_WALLETS_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "links": PAGINATION_LINKS_SCHEMA,
        "meta": PAGINATION_META_SCHEMA,
        "data": {"type": "array", "items": WALLET_RESPONSE_SCHEMA},
    },
}

# Shared Response Objects
CREATE_WALLET_RESPONSES = {
    201: OpenApiResponse(
        description="Wallet created successfully", response=WALLET_RESPONSE_SCHEMA
    ),
    400: OpenApiResponse(description="Bad request - Invalid data"),
    500: OpenApiResponse(description="Internal server error"),
}

UPDATE_WALLET_LABEL_RESPONSES = {
    200: OpenApiResponse(
        description="Wallet updated successfully", response=WALLET_RESPONSE_SCHEMA
    ),
    400: OpenApiResponse(description="Bad request - Invalid data"),
    404: OpenApiResponse(description="Wallet not found"),
    500: OpenApiResponse(description="Internal server error"),
}

DEACTIVATE_WALLET_RESPONSES = {
    200: OpenApiResponse(
        description="Wallet deactivated successfully", response=WALLET_RESPONSE_SCHEMA
    ),
    400: OpenApiResponse(description="Bad request - Invalid wallet ID"),
    404: OpenApiResponse(description="Wallet not found"),
    500: OpenApiResponse(description="Internal server error"),
}

LIST_WALLETS_RESPONSES = {
    200: OpenApiResponse(
        description="Wallets retrieved successfully with pagination",
        response=LIST_WALLETS_RESPONSE_SCHEMA,
    ),
    400: OpenApiResponse(description="Bad request - Invalid filters"),
    500: OpenApiResponse(description="Internal server error"),
}

WALLET_IDS_QUERY_PARAMETER = OpenApiParameter(
    name="wallet_ids",
    location=OpenApiParameter.QUERY,
    description="Comma-separated list of wallet UUIDs to filter by",
    required=False,
    type=str,
)

IS_ACTIVE_QUERY_PARAMETER = OpenApiParameter(
    name="is_active",
    location=OpenApiParameter.QUERY,
    description="Filter by active status (true/false)",
    required=False,
    type=bool,
)
