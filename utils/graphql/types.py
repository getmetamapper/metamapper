# -*- coding: utf-8 -*-
import graphene


class ErrorType(graphene.ObjectType):
    """Override default error type class.
    """
    resource = graphene.NonNull(graphene.String)
    field = graphene.String()
    code = graphene.NonNull(graphene.String)
