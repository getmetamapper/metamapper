# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.sso.models as models
import app.sso.schema as schema
import app.sso.serializers as serializers

import utils.mixins.mutations as mixins
import utils.graphql.scalars as utils_scalars

from django.core import exceptions

from utils.graphql.types import ErrorType
from utils.shortcuts import get_object_or_404

from app.authorization.mixins import AuthMutation
from app.authorization.permissions import WorkspaceOwnersOnly
from app.authentication.models import User, Workspace


class CreateSSOConnection(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Create a brand new SSO connection.
    """
    permission_classes = (WorkspaceOwnersOnly,)

    class Input:
        id = graphene.String(required=True)
        provider = graphene.String(required=True)
        entity_id = graphene.String(required=True)
        sso_url = graphene.String(required=False)
        default_permissions = graphene.String(required=True)
        extras = utils_scalars.JSONObject(required=False)
        x509cert = graphene.String(required=False)

    class Meta:
        serializer_class = serializers.SSOConnectionSerializer

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(workspace=info.context.workspace)

    ssoconnection = graphene.Field(schema.SSOConnectionType, name='ssoConnection')


class UpdateSSOConnection(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update an existing SSO connection associated with the workspace.
    """
    permission_classes = (WorkspaceOwnersOnly,)

    class Meta:
        serializer_class = serializers.SSOConnectionSerializer

    class Input:
        id = graphene.ID(required=True)
        is_enabled = graphene.Boolean(required=False)
        entity_id = graphene.String(required=False)
        sso_url = graphene.String(required=False)
        default_permissions = graphene.String(required=False)
        extras = utils_scalars.JSONObject(required=False)
        x509cert = graphene.String(required=False)

    ssoconnection = graphene.Field(schema.SSOConnectionType, name='ssoConnection')


class RemoveSSOConnection(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Remove a SSO connection from the workspace.
    """
    permission_classes = (WorkspaceOwnersOnly,)

    class Meta:
        serializer_class = serializers.SSOConnectionSerializer


class SetDefaultSSOConnection(AuthMutation, relay.ClientIDMutation):
    permission_classes = (WorkspaceOwnersOnly,)

    class Input:
        connection = graphene.String(required=False)

    ok = graphene.Boolean()
    errors = graphene.List(ErrorType)

    @classmethod
    def perform_mutation(cls, context, connection):
        """If none, we should disable it.
        """
        active_sso = None
        if connection:
            active_sso = get_object_or_404(models.SSOConnection, pk=connection)
        context.workspace.active_sso = active_sso
        context.workspace.save()

    @classmethod
    def mutate_and_get_payload(cls, root, info, connection=None):
        errors = None
        try:
            SetDefaultSSOConnection.perform_mutation(info.context, connection)
        except exceptions.ValidationError:
            errors = [
                ErrorType(resource='Workspace', field='active_sso', code='invalid')
            ]
        return SetDefaultSSOConnection(ok=(errors is None), errors=errors)


class CreateSSODomain(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Add an SSO domain from the workspace.
    """
    permission_classes = (WorkspaceOwnersOnly,)

    class Input:
        domain = graphene.String(required=True)

    class Meta:
        serializer_class = serializers.SSODomainSerializer

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(workspace=info.context.workspace)

    ssodomain = graphene.Field(schema.SSODomainType, name='ssoDomain')


class RemoveSSODomain(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Remove a SSO domain from the workspace.
    """
    permission_classes = (WorkspaceOwnersOnly,)

    class Meta:
        serializer_class = serializers.SSODomainSerializer


class UserExistsCheck(graphene.Mutation):
    """Confirm whether or not a user exists in our database.
    """
    class Input:
        email = graphene.String(required=True)

    ok = graphene.Boolean()
    email = graphene.String()

    is_sso_forced = graphene.Boolean(name='isSSOForced')
    workspace_slug = graphene.String()

    def mutate(self, info, email):
        """Indicates if a user exists or not.
        """
        user_exists = User.objects.filter(email__iexact=email).exists()

        is_sso_forced = False
        workspace_slug = None

        if user_exists:
            username, domain = email.split('@')
            workspace = Workspace.objects.filter(
                sso_domains__domain__iexact=domain,
                sso_domains__verified_at__isnull=False,
            ).first()

            if workspace:
                is_sso_forced = workspace.is_sso_forced
                workspace_slug = workspace.slug if is_sso_forced else None

        return UserExistsCheck(
            ok=user_exists,
            email=email,
            is_sso_forced=is_sso_forced,
            workspace_slug=workspace_slug,
        )


class TriggerSingleSignOn(graphene.Mutation):
    """Perform single sign-on action.
    """
    class Input:
        workspace_slug = graphene.String(required=True)

    redirect_url = graphene.String()

    def mutate(self, info, workspace_slug):
        """Perform the mutation.
        """
        redirect_url = None

        workspace = Workspace.objects.filter(
            slug__iexact=workspace_slug,
            active_sso_id__isnull=False,
        ).first()

        if workspace and workspace.is_sso_enabled:
            redirect_url = (
                workspace.active_sso.get_provider().get_redirect_url(info.context)
            )

        return TriggerSingleSignOn(redirect_url=redirect_url)


class Mutation(graphene.ObjectType):
    create_sso_connection = CreateSSOConnection.Field(name='createSSOConnection')
    update_sso_connection = UpdateSSOConnection.Field(name='updateSSOConnection')
    remove_sso_connection = RemoveSSOConnection.Field(name='removeSSOConnection')
    set_default_sso_connection = SetDefaultSSOConnection.Field(name='setDefaultSSOConnection')

    create_sso_domain = CreateSSODomain.Field(name='createSSODomain')
    remove_sso_domain = RemoveSSODomain.Field(name='removeSSODomain')

    user_check_exists = UserExistsCheck.Field(name='userExistsCheck')

    trigger_single_sign_on = TriggerSingleSignOn.Field()
