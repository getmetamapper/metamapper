# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.revisioner.models as models
import app.revisioner.schema as schema

import app.authorization.fields as fields
import utils.shortcuts as shortcuts

from app.definitions.models import Table


class Query(graphene.ObjectType):
    """Queries related to the revisioner models.
    """
    run = relay.Node.Field(schema.RunType)
    run_history = fields.AuthConnectionField(
        type=schema.RunType,
        datastore_id=graphene.ID(required=True),
    )

    run_revisions = fields.AuthConnectionField(
        type=schema.RevisionType,
        run_id=graphene.ID(required=True),
    )

    table_revisions = fields.AuthConnectionField(
        type=schema.RevisionType,
        table_id=graphene.ID(required=True),
    )

    def resolve_run(self, info, id, *args, **kwargs):
        """Retrieve a specific run by the global ID.
        """
        _type, pk = shortcuts.from_global_id(id)

        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': pk,
        }
        return shortcuts.get_object_or_404(models.Run, **get_kwargs)

    def resolve_run_history(self, info, datastore_id, *args, **kwargs):
        """Retrieve the last 30 active runs.
        """
        _type, pk = shortcuts.from_global_id(datastore_id)

        filter_kwargs = {
            'workspace': info.context.workspace,
            'datastore_id': pk,
            'started_at__isnull': False,
        }
        return models.Run.objects.filter(**filter_kwargs).order_by('-finished_at')

    def resolve_run_revisions(self, info, run_id, *args, **kwargs):
        """Retrieve revisions for the provided object.
        """
        _type, pk = shortcuts.from_global_id(run_id)

        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': pk,
        }

        resource = shortcuts.get_object_or_404(models.Run, **get_kwargs)

        return (
            resource.revisions
                    .filter(applied_on__isnull=False)
                    .order_by('created_at')
        )

    def resolve_table_revisions(self, info, table_id, *args, **kwargs):
        """Retrieve revisions for the provided object.
        """
        _type, pk = shortcuts.from_global_id(table_id)

        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': pk,
        }

        resource = shortcuts.get_object_or_404(Table, **get_kwargs)
        revisions = models.Revision.objects\
                          .for_model_instance(resource)\
                          .filter(applied_on__isnull=False)\
                          .exclude(metadata__field__isnull=False, metadata__field='object_id')\
                          .order_by('created_at', 'resource_type_id')
        return revisions
