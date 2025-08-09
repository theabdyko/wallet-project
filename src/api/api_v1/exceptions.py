"""
Custom exception handler for API compliance.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler that ensures proper error format.

    Args:
        exc: The exception that was raised
        context: The context in which the exception occurred

    Returns:
        Response object with proper error format
    """
    # First, try to use the DRF exception handler
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # If DRF handler doesn't handle it, use our custom format
    if isinstance(exc, Exception):
        return Response(
            {
                "errors": [
                    {
                        "status": "500",
                        "title": "Internal Server Error",
                        "detail": str(exc),
                    }
                ]
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return None
