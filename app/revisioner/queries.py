# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.revisioner.models as models
import app.revisioner.schema as schema

import app.authorization.fields as fields

import utils.errors as errors
import utils.shortcuts as shortcuts

from app.definitions import permissions as definition_permissions


class Query(graphene.ObjectType):
    """Queries related to the revisioner models.
    """
    run = relay.Node.Field(schema.RunType)

    run_history = fields.AuthConnectionField(
        type=schema.RunType,
        datastore_id=graphene.ID(required=True),
    )

    @definition_permissions.can_view_datastore_objects(lambda instance: instance.datastore)
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
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(datastore_id, True),
        }

        datastore = shortcuts.get_object_or_404(models.Datastore, **get_kwargs)

        if not definition_permissions.request_can_view_datastore(info, datastore):
            raise errors.PermissionDenied()

        return datastore.run_history.filter(started_at__isnull=False).order_by('-started_at')
