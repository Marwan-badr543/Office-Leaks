import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

from .exceptions import (
    NotFoundError,
    ValidationError,
    DuplicateResourceError,
    DatabaseError,
    ExternalServiceError,
)

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Global DRF exception handler.
    """

    response = exception_handler(exc, context)

    # Exceptions that DRF knows how to handle
    if response is not None:

        if isinstance(exc, NotFoundError):
            logger.warning("[NotFound] %s", exc.detail)

        elif isinstance(exc, ValidationError):
            logger.info("[Validation] %s", exc.detail)

        elif isinstance(exc, DuplicateResourceError):
            logger.warning("[Duplicate] %s", exc.detail)

        elif isinstance(exc, DatabaseError):
            logger.exception("[Database] %s", exc.detail)

        elif isinstance(exc, ExternalServiceError):
            logger.exception("[External Service] %s", exc.detail)

        else:
            logger.exception("[%s] %s", exc.__class__.__name__, exc.detail)

        return Response(
            {
                "success": False,
                "error": {
                    "type": exc.__class__.__name__,
                    "message": exc.detail,
                },
            },
            status=response.status_code,
        )

    # Unknown exception
    logger.exception(exc)

    return Response(
        {
            "success": False,
            "error": {
                "type": "InternalServerError",
                "message": "Something went wrong.",
            },
        },
        status=500,
    )