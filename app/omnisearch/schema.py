# -*- coding: utf-8 -*-
import graphene

from graphene.types.generic import GenericScalar


class OmnisearchResultType(graphene.ObjectType):
    """GraphQL representation of an individual search result.
    """
    label = graphene.String()

    description = graphene.String()

    pathname = graphene.String()

    tags = graphene.List(graphene.String)


class OmnisearchResultListType(graphene.ObjectType):
    """GraphQL representation of a series of search results.
    """
    pk = graphene.String()

    score = graphene.Float()

    datastore_id = graphene.String()

    model_name = graphene.String()

    search_result = graphene.Field(OmnisearchResultType)

    def resolve_search_result(instance, info):
        pk = instance['pk']
        if instance['model_name'] in ('Table', 'Column'):
            pk = int(instance['pk'])
        return info.context.loaders.omnisearch_results.load((pk, instance['model_name']))

    def resolve_pk(instance, info):
        return instance['pk']

    def resolve_score(instance, info):
        return instance['score']

    def resolve_datastore_id(instance, info):
        return instance['datastore_id']

    def resolve_model_name(instance, info):
        return instance['model_name']


class OmnisearchResponseType(graphene.ObjectType):
    """Parent response type for all omnisearch results.
    """
    results = graphene.List(OmnisearchResultListType)

    facets = graphene.Field(GenericScalar)

    elapsed = graphene.Float()
