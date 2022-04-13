# -*- coding: utf-8 -*-
import graphene
import graphene_django.debug as debug

import app.authentication.graphql as authentication
import app.authorization.graphql as authorization
import app.api.graphql as api
import app.audit.graphql as audit
import app.checks.graphql as checks
import app.comments.graphql as comments
import app.customfields.graphql as customfields
import app.definitions.graphql as definitions
import app.omnisearch.graphql as omnisearch
import app.sso.graphql as sso
import app.revisioner.graphql as revisioner

from django.conf import settings


class HealthCheck(graphene.Mutation):
    """Check to see if GraphQL is working...
    """
    ok = graphene.Boolean()

    def mutate(self, info):
        return HealthCheck(ok=True)


class Query(authentication.Query,
            authorization.Query,
            api.Query,
            audit.Query,
            checks.Query,
            comments.Query,
            customfields.Query,
            definitions.Query,
            omnisearch.Query,
            sso.Query,
            revisioner.Query,
            graphene.ObjectType):
    """Global Query accessor.
    """
    if settings.DEBUG:
        debug = graphene.Field(debug.DjangoDebug, name='__debug')

    beacon_activated = graphene.Boolean()

    def resolve_beacon_activated(self, *args, **kwargs):
        """bool: Indicates if the beacon is active or not for this installation.
        """
        return settings.METAMAPPER_BEACON_ACTIVATED


class Mutation(authentication.Mutation,
               authorization.Mutation,
               api.Mutation,
               checks.Mutation,
               comments.Mutation,
               customfields.Mutation,
               definitions.Mutation,
               sso.Mutation,
               graphene.ObjectType):
    """Global Mutation accessor.
    """
    healthcheck = HealthCheck.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
