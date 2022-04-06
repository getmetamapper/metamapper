# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.authorization.permissions as permissions

import app.api.schema as schema
import app.api.serializers as serializers

import utils.mixins.mutations as mixins


class CreateApiToken(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Create an API token scoped to a workspace.
    """
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    class Input:
        name = graphene.String(required=True)
        is_enabled = graphene.Boolean(required=False, default_value=True)

    class Meta:
        serializer_class = serializers.ApiTokenSerializer

    token = graphene.Field(graphene.String)

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(workspace=info.context.workspace)

    api_token = graphene.Field(schema.ApiTokenType)

    secret = graphene.Field(graphene.String)

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        secret = None
        if instance:
            secret = instance.get_secret()
        return_kwargs = {
            'api_token': instance,
            'secret': secret,
            'errors': errors,
        }
        return cls(**return_kwargs)


class UpdateApiToken(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update an existing API token resource.
    """
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    class Input:
        id = graphene.ID(required=True)
        is_enabled = graphene.Boolean(required=False)

    class Meta:
        serializer_class = serializers.ApiTokenSerializer

    api_token = graphene.Field(schema.ApiTokenType)

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'api_token': instance,
            'errors': errors,
        }
        return cls(**return_kwargs)


class DeleteApiToken(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Delete an existing API token resource.
    """
    permission_classes = (permissions.WorkspaceOwnersOnly,)

    class Input:
        id = graphene.ID(required=True)

    class Meta:
        serializer_class = serializers.ApiTokenSerializer


class Mutation(graphene.ObjectType):
    """Mutations for managing API resources.
    """
    create_api_token = CreateApiToken.Field()
    update_api_token = UpdateApiToken.Field()
    delete_api_token = DeleteApiToken.Field()
