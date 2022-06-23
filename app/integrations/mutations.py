# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.authorization.permissions as permissions

import app.integrations.schema as schema
import app.integrations.serializers as serializers

import utils.graphql.scalars as scalars
import utils.mixins.mutations as mixins


class CreateIntegrationConfig(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Create an integration configuration scoped to a workspace.
    """
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    class Input:
        integration = graphene.String(required=True)
        meta = scalars.JSONObject(required=True)

    class Meta:
        serializer_class = serializers.IntegrationConfigSerializer

    integration_config = graphene.Field(schema.IntegrationConfigType)

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(workspace=info.context.workspace, user=info.context.user)

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'integration_config': instance,
            'errors': errors,
        }
        return cls(**return_kwargs)


class UpdateIntegrationConfig(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update an existing integration configuration.
    """
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    class Input:
        id = graphene.ID(required=True)
        meta = scalars.JSONObject(required=False)

    class Meta:
        serializer_class = serializers.IntegrationConfigSerializer

    integration_config = graphene.Field(schema.IntegrationConfigType)

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'integration_config': instance,
            'errors': errors,
        }
        return cls(**return_kwargs)


class DeleteIntegrationConfig(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Delete an existing integration configuration.
    """
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    class Input:
        id = graphene.ID(required=True)

    class Meta:
        serializer_class = serializers.IntegrationConfigSerializer


class Mutation(graphene.ObjectType):
    """Mutations for managing integrations.
    """
    create_integration_config = CreateIntegrationConfig.Field()
    update_integration_config = UpdateIntegrationConfig.Field()
    delete_integration_config = DeleteIntegrationConfig.Field()
