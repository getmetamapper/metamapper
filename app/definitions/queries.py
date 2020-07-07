# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.definitions.models as models
import app.definitions.schema as schema
import app.definitions.permissions as permissions

import utils.errors as errors
import utils.shortcuts as shortcuts

from graphene.types.generic import GenericScalar
from guardian.shortcuts import get_users_with_perms, get_groups_with_perms

from app.authorization.fields import AuthConnectionField
from app.authorization import permissions as auth_perms


class Query(graphene.ObjectType):
    """Queries related to the definitions models.
    """
    datastores = AuthConnectionField(
        type=schema.DatastoreType,
        search=graphene.String(required=False),
    )

    datastore_engines = graphene.List(GenericScalar)

    datastore = graphene.Field(
        type=schema.DatastoreType,
        id=graphene.ID(required=True),
    )

    datastore_by_slug = graphene.Field(
        type=schema.DatastoreType,
        slug=graphene.String(required=True),
    )

    table_definition = graphene.Field(
        type=schema.TableType,
        datastore_id=graphene.ID(required=True),
        schema_name=graphene.String(required=True),
        table_name=graphene.String(required=True),
    )

    datastore_user_access_privileges = graphene.List(
        of_type=schema.DatastoreUserGranteeType,
        datastore_id=graphene.ID(required=True),
    )

    datastore_group_access_privileges = graphene.List(
        of_type=schema.DatastoreGroupGranteeType,
        datastore_id=graphene.ID(required=True),
    )

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_datastores(self, info, search=None, *args, **kwargs):
        """Retrieve a list of datastores.
        """
        queryset = models.Datastore.search_objects.execute(
            search=search,
            workspace=info.context.workspace,
            **kwargs,
        )

        # Owners have access to all objects in Metamapper
        if info.context.user.is_owner(info.context.workspace.id):
            return queryset

        return permissions.get_datastores_for_user(queryset, info.context.user)

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

    @permissions.can_view_datastore_objects()
    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_datastore(self, info, id):
        """Retrieve a single datastore by ID.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(id, True),
        }
        return shortcuts.get_object_or_404(models.Datastore, **get_kwargs)

    @permissions.can_view_datastore_objects()
    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_datastore_by_slug(self, info, slug):
        """Retrieve a single datastore by slug.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'slug__iexact': slug,
        }
        return shortcuts.get_object_or_404(models.Datastore, **get_kwargs)

    @permissions.can_view_datastore_objects(lambda instance: instance.datastore)
    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_table_definition(self, info, datastore_id, schema_name, table_name, **kwargs):
        """Retrieve detailed table definition.
        """
        get_kwargs = {
            'name__iexact': table_name,
            'schema__datastore_id': shortcuts.from_global_id(datastore_id, True),
            'schema__name__iexact': schema_name,
            'workspace': info.context.workspace,
        }
        return shortcuts.get_object_or_404(models.Table, **get_kwargs)

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_datastore_user_access_privileges(self, info, datastore_id):
        """Retrieve users and their permissions for the given datastore.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(datastore_id, True),
        }

        datastore = shortcuts.get_object_or_404(models.Datastore, **get_kwargs)

        if not permissions.request_can_view_datastore(info, datastore):
            raise errors.PermissionDenied()

        users = get_users_with_perms(
            obj=datastore,
            attach_perms=True,
            with_group_users=False,
        )

        return [
            {'name': user.name, 'privileges': privileges, 'pk': user.pk}
            for user, privileges in users.items()
        ]

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_datastore_group_access_privileges(self, info, datastore_id):
        """Retrieve users and their permissions for the given datastore.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(datastore_id, True),
        }

        datastore = shortcuts.get_object_or_404(models.Datastore, **get_kwargs)

        if not permissions.request_can_view_datastore(info, datastore):
            raise errors.PermissionDenied()

        groups = get_groups_with_perms(
            obj=datastore,
            attach_perms=True,
        )

        return [
            {'name': group.name, 'privileges': privileges, 'pk': group.pk}
            for group, privileges in groups.items()
        ]
