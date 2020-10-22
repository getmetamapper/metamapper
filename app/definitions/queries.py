# -*- coding: utf-8 -*-
import graphene

import app.definitions.models as models
import app.definitions.schema as schema
import app.definitions.filters as filters
import app.definitions.permissions as permissions
import app.inspector.service as inspector

import utils.errors as errors
import utils.shortcuts as shortcuts

from django.core.cache import cache
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

    column_definition = graphene.Field(
        type=schema.ColumnType,
        datastore_id=graphene.ID(required=True),
        schema_name=graphene.String(required=True),
        table_name=graphene.String(required=True),
        column_name=graphene.String(required=True),
    )

    datastore_user_access_privileges = graphene.List(
        of_type=schema.DatastoreUserGranteeType,
        datastore_id=graphene.ID(required=True),
    )

    datastore_group_access_privileges = graphene.List(
        of_type=schema.DatastoreGroupGranteeType,
        datastore_id=graphene.ID(required=True),
    )

    datastore_assets = AuthConnectionField(
        type=schema.TableType,
        slug=graphene.String(required=True),
        search=graphene.String(required=False),
        filterset_class=filters.DataAssetsFilterSet,
    )

    schema_names_by_datastore = graphene.List(
        of_type=graphene.String,
        datastore_id=graphene.ID(required=True),
    )

    table_names_by_schema = graphene.List(
        of_type=graphene.String,
        datastore_id=graphene.ID(required=True),
        schema_name=graphene.String(required=True),
    )

    table_last_commit_timestamp = graphene.Field(
        type=graphene.String,
        datastore_id=graphene.ID(required=True),
        schema_name=graphene.String(required=True),
        table_name=graphene.String(required=True),
    )

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_datastores(self, info, search=None, *args, **kwargs):
        """Retrieve a list of datastores.
        """
        queryset = models.Datastore.search_objects.execute(
            search=search,
            workspace=info.context.workspace,
            deleted_at__isnull=True,
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

    @permissions.can_view_datastore_objects(lambda instance: instance.datastore)
    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_column_definition(self, info, datastore_id, schema_name, table_name, column_name, **kwargs):
        """Retrieve detailed column definition.
        """
        get_kwargs = {
            'name__iexact': column_name,
            'table__schema__datastore_id': shortcuts.from_global_id(datastore_id, True),
            'table__schema__name__iexact': schema_name,
            'table__name__iexact': table_name,
            'workspace': info.context.workspace,
        }
        return shortcuts.get_object_or_404(models.Column, **get_kwargs)

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
            {'name': user.display_name, 'privileges': privileges, 'pk': user.pk}
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

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_datastore_assets(self, info, slug, search=None, *args, **kwargs):
        """Retrieve the assets for this datastore.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'slug__iexact': slug,
        }

        datastore = shortcuts.get_object_or_404(models.Datastore, **get_kwargs)

        if not permissions.request_can_view_datastore(info, datastore):
            raise errors.PermissionDenied()

        queryset = models.Table.search_objects.execute(
            search=search,
            schema__datastore_id=datastore.id,
        )

        return queryset.order_by('schema__name', 'name')

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_schema_names_by_datastore(self, info, datastore_id, *args, **kwargs):
        """Retrieve a list of schema names for the provided datastore.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(datastore_id, True),
        }

        datastore = shortcuts.get_object_or_404(models.Datastore, **get_kwargs)

        if not permissions.request_can_view_datastore(info, datastore):
            raise errors.PermissionDenied()

        return sorted(datastore.schemas.values_list('name', flat=True))

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_table_names_by_schema(self, info, datastore_id, schema_name, **kwargs):
        """Retrieve a list of table names for the provided schema.
        """
        get_kwargs = {
            'name__iexact': schema_name,
            'datastore_id': shortcuts.from_global_id(datastore_id, True),
            'workspace': info.context.workspace,
        }

        schema = shortcuts.get_object_or_404(models.Schema, **get_kwargs)

        if not permissions.request_can_view_datastore(info, schema.datastore):
            raise errors.PermissionDenied()

        return sorted(schema.tables.values_list('name', flat=True))

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_table_last_commit_timestamp(self, info, datastore_id, schema_name, table_name, **kwargs):
        """Retrieve the last time a table was modified.
        """
        get_kwargs = {
            'name__iexact': table_name,
            'schema__datastore_id': shortcuts.from_global_id(datastore_id, True),
            'schema__name__iexact': schema_name,
            'workspace': info.context.workspace,
        }

        table = shortcuts.get_object_or_404(models.Table, **get_kwargs)

        if not permissions.request_can_view_datastore(info, table.datastore):
            raise errors.PermissionDenied()

        ca_id = "table.last_commit.%s" % table.id
        value = cache.get(ca_id)

        if value is not None:
            return value

        value = (
            inspector.get_engine(table.datastore)
                     .get_last_commit_time_for_table(schema_name, table_name)
        )

        cache.set(ca_id, value, (15 * 60))

        return value
