# -*- coding: utf-8 -*-
import logging


class GraphQLLocatedErrorFilter(logging.Filter):
    """Filter out annoying GraphQLLocatedError stack traces.
    """
    def filter(self, record):
        if 'graphql.error.located_error.GraphQLLocatedError:' in record.msg:
            return False
        return True
