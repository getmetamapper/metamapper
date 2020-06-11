# -*- coding: utf-8 -*-
import logging


class SuppressGraphqlErrorFilter(logging.Filter):
    """Filter out annoying GraphQLLocatedError stack traces.
    """
    def filter(self, record):
        if 'graphql.error.located_error.GraphQLLocatedError' in record.msg:
            return False
        if 'graphql_jwt.exceptions.JSONWebTokenError' in record.msg:
            return False
        if 'jwt.exceptions.InvalidAudienceError' in record.msg:
            return False
        return True
