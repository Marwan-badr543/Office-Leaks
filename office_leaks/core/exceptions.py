from rest_framework.exceptions import APIException
from rest_framework import status


class AppException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Application error."
    default_code = "application_error"


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found."


class ValidationError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation failed."


class DuplicateResourceError(AppException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource already exists."


class DatabaseError(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Database operation failed."


class ExternalServiceError(AppException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "External service unavailable."