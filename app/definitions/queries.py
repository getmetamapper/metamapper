# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.definitions.models as models
import app.definitions.schema as schema

import utils.shortcuts as shortcuts

from graphene.types.generic import GenericScalar

from app.authorization.fields import AuthConnectionField


class Query(graphene.ObjectType):
    """Queries related to the definitions models.
    """
    datastore = relay.Node.Field(schema.DatastoreType)

    datastore_engines = graphene.List(GenericScalar)

    datastore_by_slug = graphene.Field(
        type=schema.DatastoreType,
        slug=graphene.String(required=True),
    )

    datastores = AuthConnectionField(
        type=schema.DatastoreType,
        search=graphene.String(required=False),
    )

    table_definition = graphene.Field(
        type=schema.TableType,
        datastore_id=graphene.ID(required=True),
        schema_name=graphene.String(required=True),
        table_name=graphene.String(required=True),
    )

    def resolve_datastores(self, info, search=None, *args, **kwargs):
        """Retrieve a list of datastores.
        """
        return models.Datastore.search_objects.execute(
            search=search,
            workspace=info.context.workspace,
            **kwargs,
        )

    def resolve_datastore_engines(self, info):
        """Return the supported datastore engines.
        """
        return [
            {
                'dialect': dialect,
                'label': label,
            }
            for dialect, label in models.Datastore.ENGINE_CHOICES
        ]

    def resolve_datastore(self, info, id):
        """Retrieve a single datastore by ID.
        """
        _type, pk = shortcuts.from_global_id(id)
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': pk,
        }
        return shortcuts.get_object_or_404(models.Datastore, **get_kwargs)

    def resolve_datastore_by_slug(self, info, slug):
        """Retrieve a single datastore by slug.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'slug': slug,
        }
        return shortcuts.get_object_or_404(models.Datastore, **get_kwargs)

    def resolve_table_definition(self, info, datastore_id, schema_name, table_name, **kwargs):
        """Retrieve detailed table definition.
        """
        _type, pk = shortcuts.from_global_id(datastore_id)
        get_kwargs = {
            'name__iexact': table_name,
            'schema__datastore_id': pk,
            'schema__name__iexact': schema_name,
            'workspace': info.context.workspace,
        }
        return shortcuts.get_object_or_404(models.Table, **get_kwargs)
