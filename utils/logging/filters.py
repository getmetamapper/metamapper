# -*- coding: utf-8 -*-
import logging


class SuppressGraphqlErrorFilter(logging.Filter):
    """Filter out annoying GraphQLLocatedError stack traces.
    """
    excluded_error_classes = [
        'graphql.error.located_error.GraphQLLocatedError',
        'graphql_jwt.exceptions.JSONWebTokenError',
        'jwt.exceptions.InvalidAudienceError',
        'jwt.exceptions.InvalidSignatureError',
    ]

    def filter(self, record):
        for error_class in self.excluded_error_classes:
            if error_class in record.msg:
                return False
        return True
