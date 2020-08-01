# -*- coding: utf-8 -*-
import graphene

import app.audit.models as models
import app.audit.schema as schema
import app.authorization.fields as fields

import utils.shortcuts as shortcuts


class Query(graphene.ObjectType):
    """Queries related to the definitions models.
    """
    recent_datastore_activities = fields.AuthConnectionField(
        type=schema.AuditActivityType,
        datastore_id=graphene.ID(required=True),
    )

    recent_user_activities = fields.AuthConnectionField(
        type=schema.AuditActivityType,
        user_id=graphene.ID(required=True),
    )

    def resolve_recent_datastore_activities(self, info, datastore_id, *args, **kwargs):
        """Retrieve recent actions associated with a specific datastore.
        """
        _type, pk = shortcuts.from_global_id(datastore_id)

        filter_kwargs = {
            'workspace': info.context.workspace,
            'extras__datastore_id': pk,
        }

        return (
            models.Activity
                  .objects
                  .filter(**filter_kwargs)
                  .order_by('-timestamp')
        )

    def resolve_recent_user_activities(self, info, user_id, *args, **kwargs):
        """Retrieve recent actions peformed by a specific user.
        """
        _type, pk = shortcuts.from_global_id(user_id)

        filter_kwargs = {
            'workspace': info.context.workspace,
            'actor_id': pk,
        }

        return (
            models.Activity
                  .objects
                  .filter(**filter_kwargs)
                  .order_by('-timestamp')
        )
