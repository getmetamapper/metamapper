# -*- coding: utf-8 -*-
from django.core import exceptions
from graphql import GraphQLError


class PermissionDeniedError(GraphQLError):
    default_message = 'Permission denied'

    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = self.default_message
        return super().__init__(message=message, *args, **kwargs)


class ValidationError(exceptions.ValidationError):
    """Default validation error class.
    """


class PasswordResetTokenExpired(ValidationError):
    """Thrown when a password reset token as expired.
    """


class CannotDeleteDefaultConnection(ValidationError):
    """You cannot delete the default SSO connection.
    """
