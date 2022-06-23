# -*- coding: utf-8 -*-
import graphene

import utils.shortcuts as shortcuts

import app.integrations.schema as schema
import app.integrations.models as models
import app.integrations.registry as registry

from app.authorization.fields import AuthConnectionField
from app.authorization import permissions as auth_perms


class Query(graphene.ObjectType):
    """Queries related to the integrations models.
    """
    available_integrations = graphene.List(schema.IntegrationType)

    integration = graphene.Field(schema.IntegrationType, id=graphene.String(required=True))

    integration_config = graphene.Field(schema.IntegrationConfigType, id=graphene.ID(required=True))
    integration_configs = AuthConnectionField(
        type=schema.IntegrationConfigType,
        integration=graphene.String(required=False),
    )

    @auth_perms.login_required
    def resolve_available_integrations(self, info):
        """Retrieve available integrations.
        """
        return registry.get_available_integrations(info.context.workspace)

    @auth_perms.login_required
    def resolve_integration(self, info, id):
        """Retrieve integration from available integrations.
        """
        return registry.get_integration(info.context.workspace, id.upper())

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_integration_config(self, info, id):
        """Retrieve a single integration by ID.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(id, True),
        }
        return shortcuts.get_object_or_404(models.IntegrationConfig, **get_kwargs)

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_integration_configs(self, info, integration=None, *args, **kwargs):
        """Retrieve a list of integrations associated with a datastore.
        """
        queryset = models.IntegrationConfig.objects.filter(workspace=info.context.workspace)

        if integration:
            queryset = queryset.filter(integration__iexact=integration)

        return queryset.order_by('created_at')
