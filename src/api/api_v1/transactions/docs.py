"""
OpenAPI schemas and examples for transaction endpoints.

This module centralizes all OpenAPI documentation for transaction endpoints,
ensuring consistency and reusability across the API.
"""
# Third-party imports
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse

# Shared Response Schemas
TRANSACTION_ATTRIBUTES_SCHEMA = {
    "type": "object",
    "properties": {
        "wallet_id": {"type": "string", "format": "uuid"},
        "txid": {"type": "string"},
        "amount": {"type": "integer"},
        "is_active": {"type": "boolean"},
        "deactivated_at": {"type": "string", "format": "date-time", "nullable": True},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
    },
}

TRANSACTION_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "example": "transactions"},
        "id": {"type": "string", "format": "uuid"},
        "attributes": TRANSACTION_ATTRIBUTES_SCHEMA,
    },
}

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
TRANSACTION_LIST_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "links": PAGINATION_LINKS_SCHEMA,
        "meta": PAGINATION_META_SCHEMA,
        "data": {"type": "array", "items": TRANSACTION_RESPONSE_SCHEMA},
    },
}

# Shared Request Examples
CREATE_TRANSACTION_REQUEST_EXAMPLE = OpenApiExample(
    "Request Example",
    value={
        "data": {
            "type": "transactions",
            "attributes": {
                "wallet_id": "123e4567-e89b-12d3-a456-426614174000",
                "amount": 1000,
            },
        }
    },
    request_only=True,
)

# Shared Response Examples
CREATE_TRANSACTION_SUCCESS_EXAMPLE = OpenApiExample(
    "Success Response",
    value={
        "data": {
            "type": "transactions",
            "id": "456e7890-e89b-12d3-a456-426614174001",
            "attributes": {
                "wallet_id": "123e4567-e89b-12d3-a456-426614174000",
                "txid": "tx_123456789",
                "amount": 1000,
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

GET_TRANSACTION_SUCCESS_EXAMPLE = OpenApiExample(
    "Success Response",
    value={
        "data": {
            "type": "transactions",
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "attributes": {
                "wallet_id": "123e4567-e89b-12d3-a456-426614174001",
                "txid": "abc123def456",
                "amount": 1000000000000000000,
                "is_active": True,
                "deactivated_at": None,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
            },
        }
    },
    response_only=True,
    status_codes=["200"],
)

# Shared Response Objects
CREATE_TRANSACTION_RESPONSES = {
    201: OpenApiResponse(
        description="Transaction created successfully",
        response=TRANSACTION_RESPONSE_SCHEMA,
    ),
    400: OpenApiResponse(description="Bad request - Invalid data"),
    404: OpenApiResponse(description="Wallet not found"),
    409: OpenApiResponse(description="Transaction with this txid already exists"),
    500: OpenApiResponse(description="Internal server error"),
}

GET_TRANSACTION_RESPONSES = {
    200: OpenApiResponse(
        description="Transaction found", response=TRANSACTION_RESPONSE_SCHEMA
    ),
    404: OpenApiResponse(description="Transaction not found"),
    400: OpenApiResponse(description="Invalid txid format"),
    500: OpenApiResponse(description="Internal server error"),
}

LIST_TRANSACTIONS_RESPONSES = {
    200: OpenApiResponse(
        description="Transactions retrieved successfully",
        response=TRANSACTION_LIST_RESPONSE_SCHEMA,
    ),
    400: OpenApiResponse(description="Bad request - Invalid filters"),
    500: OpenApiResponse(description="Internal server error"),
}

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
    description='Field to sort by. Prefix with "-" for descending order. Default: transactions sorted by created_at in descending order (newest first).',
    required=False,
    type=str,
    examples=[
        OpenApiExample("Created date ascending", value="created_at"),
        OpenApiExample("Created date descending", value="-created_at"),
        OpenApiExample("Amount ascending", value="amount"),
        OpenApiExample("Amount descending", value="-amount"),
        OpenApiExample("Transaction ID ascending", value="txid"),
        OpenApiExample("Transaction ID descending", value="-txid"),
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
LIST_TRANSACTIONS_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "links": PAGINATION_LINKS_SCHEMA,
        "meta": PAGINATION_META_SCHEMA,
        "data": {"type": "array", "items": TRANSACTION_RESPONSE_SCHEMA},
    },
}

# Shared Parameters
WALLET_IDS_QUERY_PARAMETER = OpenApiParameter(
    name="wallet_ids",
    location=OpenApiParameter.QUERY,
    description="Comma-separated list of wallet UUIDs to filter by",
    required=False,
    type=str,
    examples=[
        OpenApiExample("Single wallet", value="123e4567-e89b-12d3-a456-426614174000"),
        OpenApiExample(
            "Multiple wallets",
            value="123e4567-e89b-12d3-a456-426614174000,456e7890-e89b-12d3-a456-426614174001",
        ),
    ],
)

TXID_PATH_PARAMETER = OpenApiParameter(
    name="txid",
    location=OpenApiParameter.PATH,
    description="External transaction ID",
    required=True,
    type=str,
    examples=[
        OpenApiExample("Valid txid", value="abc123def456"),
        OpenApiExample("Another txid", value="xyz789abc123"),
    ],
)
