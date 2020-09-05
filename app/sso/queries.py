# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import utils.shortcuts as shortcuts

from graphene.types.generic import GenericScalar
from app.authorization.permissions import login_required

from app.authorization.fields import AuthConnectionField

from app.sso.models import SSOConnection, SSODomain
from app.sso.schema import SSOConnectionType, SSODomainType


class Query(graphene.ObjectType):
    """Queries related to the SSO models.
    """
    sso_connection = relay.Node.Field(SSOConnectionType)
    sso_connections = AuthConnectionField(SSOConnectionType)

    sso_connection_by_primary_key = graphene.Field(
        type=SSOConnectionType,
        pk=graphene.String(required=True),
    )

    sso_domain = relay.Node.Field(SSODomainType)
    sso_domains = AuthConnectionField(SSODomainType)

    sso_providers = graphene.List(GenericScalar)
    sso_primary_key = graphene.Field(graphene.String)

    github_organizations = graphene.Field(GenericScalar)

    @login_required
    def resolve_sso_connections(self, info, *args, **kwargs):
        """Retrieve a list of datastores.
        """
        return info.context.workspace.sso_connections.order_by('created_at')

    @login_required
    def resolve_sso_connection(self, info, id):
        """Retrieve a single sso connection by ID.
        """
        _type, pk = shortcuts.from_global_id(id)
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': pk,
        }
        return shortcuts.get_object_or_404(SSOConnection, **get_kwargs)

    @login_required
    def resolve_sso_connection_by_primary_key(self, info, pk):
        """Find SSO connection by primary key.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': pk,
        }
        return shortcuts.get_object_or_404(SSOConnection, **get_kwargs)

    @login_required
    def resolve_sso_domains(self, info, *args, **kwargs):
        """Retrieve a list of datastores.
        """
        return info.context.workspace.sso_domains.order_by('domain')

    @login_required
    def resolve_sso_domain(self, info, id):
        """Retrieve a single sso domain by ID.
        """
        _type, pk = shortcuts.from_global_id(id)

        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': pk,
        }
        return shortcuts.get_object_or_404(SSODomain, **get_kwargs)

    def resolve_sso_providers(self, info):
        """Return the available SSO providers.
        """
        return [
            {
                'clientId': SSOConnection.get_client_id(provider),
                'label': label,
                'protocol': SSOConnection.get_protocol(provider),
                'provider': provider,
            }
            for provider, label in SSOConnection.PROVIDER_CHOICES
            if SSOConnection.provider_is_enabled(provider)
        ]

    @login_required
    def resolve_sso_primary_key(self, info):
        """Return an unreserved PK for an SSO connection.
        """
        return SSOConnection.generate_primary_key(downcase=True)

    @login_required
    def resolve_github_organizations(self, info):
        """Retrieve the Github organizations associated with this user.
        """
        return info.context.user.get_github_organizations()
