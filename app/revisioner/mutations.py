# -*- coding: utf-8 -*-
import graphene

import app.authorization.permissions as permissions
import app.authorization.mixins as mixins
import app.definitions.models as models
import app.revisioner.tasks.v1.scheduler as scheduler

import utils.errors as err
import utils.graphql.types as types
import utils.shortcuts as shortcuts


class QueueRevisionerRun(mixins.AuthMutation, graphene.Mutation):
    """Queue a revisioner run for the provided datastore.
    """
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    class Input:
        datastore_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(types.ErrorType)

    @classmethod
    def mutate(cls, root, info, datastore_id):
        """Check permissions and perform the mutation.
        """
        if not cls.has_permission(root, info, datastore_id):
            raise err.PermissionDenied()

        datastore = shortcuts.get_object_or_404(
            models.Datastore,
            workspace=info.context.workspace,
            pk=shortcuts.from_global_id(datastore_id, True),
        )

        run = datastore.most_recent_run

        if run and not run.finished:
            errors = [
                types.ErrorType(resource='Run', field='finished', code='invalid')
            ]
            return cls(ok=False, errors=errors)

        runs = scheduler.create_runs(datastore_slug=datastore.slug)

        if len(runs):
            scheduler.queue_runs(datastore.slug, countdown_in_minutes=0)

        return cls(ok=True, errors=None)


class Mutation(graphene.ObjectType):
    queue_revisioner_run = QueueRevisionerRun.Field()
