# -*- coding: utf-8 -*-
from django.core import exceptions
from graphql import GraphQLError


class MetamapperGraphQLError(GraphQLError):
    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = self.default_message
        return super().__init__(message=message, *args, **kwargs)


class PermissionDenied(MetamapperGraphQLError):
    default_message = 'Permission denied'
    status_code = 403


class NotFound(MetamapperGraphQLError):
    default_message = 'Resource not found'
    status_code = 404


class SubscriptionExpired(MetamapperGraphQLError):
    default_message = 'Subscription expired'
    status_code = 402


class WorkspaceSuspended(MetamapperGraphQLError):
    default_message = 'Workspace suspended'
    status_code = 423


class ValidationError(exceptions.ValidationError):
    """Default validation error class.
    """


class PasswordResetTokenExpired(ValidationError):
    """Thrown when a password reset token as expired.
    """


class CannotDeleteDefaultConnection(ValidationError):
    """You cannot delete the default SSO connection.
    """


def format_error(error):
    try:
        message = str(error)
    except UnicodeEncodeError:
        message = error.message.encode("utf-8")
    formatted_error = {"message": message}
    if isinstance(error, GraphQLError):
        if error.locations is not None:
            formatted_error["locations"] = [
                {"line": loc.line, "column": loc.column} for loc in error.locations
            ]
        if error.path is not None:
            formatted_error["path"] = error.path

        if error.extensions is not None:
            formatted_error["extensions"] = error.extensions

        formatted_error["status"] = 400

        if hasattr(error, "original_error"):
            formatted_error["status"] = getattr(error.original_error, "status_code", 400)

    return formatted_error
