# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.definitions.models as models

import utils.connections as connections
import utils.shortcuts as shortcuts

from django.forms.models import model_to_dict

from graphene_django import DjangoObjectType
from graphene.types.generic import GenericScalar

from app.revisioner.schema import RunType

from app.authorization.mixins import AuthNode
from app.authorization.permissions import WorkspaceTeamMembersOnly


class ColumnType(AuthNode, DjangoObjectType):
    """GraphQL representation of a Column.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    pk = graphene.Int()

    comments_count = graphene.Int()
    full_data_type = graphene.String()

    class Meta:
        model = models.Column
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        exclude_fields = []

    @classmethod
    def get_node(cls, info, id):
        """We should only return columns related to the current workspace.
        """
        return models.Column.objects.filter(
            workspace=info.context.workspace,
            id=id,
        ).first()

    def resolve_comments_count(instance, info):
        """Counter of the existing comments on the column.
        """
        return info.context.loaders.column_comment_counts.load(instance.pk)

    def resolve_full_data_type(instance, info):
        """Decorated version of the `data_type` field.
        """
        return instance.full_data_type


class OwnerType(graphene.ObjectType):
    """GraphQL representation of a data asset owner.
    """
    id = graphene.ID()
    pk = GenericScalar()
    name = graphene.String()
    type = graphene.String()

    avatar_url = graphene.String()

    def resolve_id(root, info):
        return shortcuts.to_global_id(f'{root.__class__.__name__}Type', root.pk)

    def resolve_pk(root, info):
        return root.id

    def resolve_avatar_url(root, info):
        return root.avatar_url


class AssetOwnerType(AuthNode, DjangoObjectType):
    """GraphQL representation of a AssetOwner.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    type = graphene.String()

    owner = graphene.Field(OwnerType)

    class Meta:
        model = models.AssetOwner
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        exclude_fields = []

    @classmethod
    def get_node(cls, info, id):
        """We should only return owners related to the current workspace.
        """
        return models.AssetOwner.objects.filter(
            workspace=info.context.workspace,
            id=id,
        ).first()

    def resolve_type(root, info):
        """str: Type of the owner being returned.
        """
        return root.owner.__class__.__name__.upper()


class TableType(AuthNode, DjangoObjectType):
    """GraphQL representation of a Table.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    pk = graphene.Int()

    properties = GenericScalar()

    schema = graphene.Field('app.definitions.schema.SchemaType')
    owners = graphene.List(AssetOwnerType)

    class Meta:
        model = models.Table
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        exclude_fields = []

    @classmethod
    def get_node(cls, info, id):
        """We should only return tables related to the current workspace.
        """
        return models.Table.objects.filter(
            workspace=info.context.workspace,
            id=id,
        ).first()

    def resolve_kind(instance, info):
        """Capitalize the `kind` attribute.
        """
        return instance.kind[0].upper() + instance.kind[1:].lower()

    def resolve_columns(instance, info):
        """Should return the associated Columns.
        """
        return info.context.loaders.table_columns.load(instance.object_id)

    def resolve_schema(instance, info):
        return info.context.loaders.table_schemas.load(instance.schema_id)

    def resolve_owners(instance, info):
        return instance.owners.order_by('order').prefetch_related('owner')


class SchemaType(AuthNode, DjangoObjectType):
    """GraphQL representation of a Datastore.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    pk = graphene.Int()

    tables = graphene.List(TableType, first=graphene.Int(required=False))

    class Meta:
        model = models.Schema
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        exclude_fields = []

    @classmethod
    def get_node(cls, info, id):
        """We should only return schemas related to the current workspace.
        """
        return models.Schema.objects.filter(
            workspace=info.context.workspace,
            id=id,
        ).first()

    def resolve_tables(instance, info, first=None):
        """Retrieve all of the Table objects associated with this Schema.
        """
        return info.context.loaders.schema_tables.load(instance.object_id)


class JdbcConnectionType(graphene.ObjectType):
    """GraphQL representation of a JDBC connection.
    """
    engine = graphene.String()
    host = graphene.String()
    username = graphene.String()
    database = graphene.String()
    port = graphene.Int()
    extras = GenericScalar()


class SSHTunnelConfigType(graphene.ObjectType):
    """GraphQL representation of SSH tunnel configuration.
    """
    is_enabled = graphene.Boolean()
    host = graphene.String()
    user = graphene.String()
    port = graphene.Int()
    public_key = graphene.String()


class DatastoreIntervalType(graphene.ObjectType):
    """GraphQL representation of a Datastore interval.
    """
    label = graphene.String()
    value = graphene.String()

    def resolve_label(value, info):
        return shortcuts.humanize_timedelta(value)

    def resolve_value(value, info):
        return value


class DatastoreType(AuthNode, DjangoObjectType):
    """GraphQL representation of a Datastore.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    jdbc_connection = graphene.Field(JdbcConnectionType)

    ssh_config = graphene.Field(SSHTunnelConfigType)

    schemas = graphene.List(SchemaType, first=graphene.Int(required=False))

    interval = graphene.Field(DatastoreIntervalType)

    latest_run = graphene.Field(RunType)

    first_run_is_pending = graphene.Boolean()

    class Meta:
        model = models.Datastore
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        only_fields = (
            'id',
            'pk',
            'name',
            'slug',
            'is_enabled',
            'version',
            'interval',
            'short_desc',
            'tags',
            'jdbc_connection',
            'object_permissions_enabled',
            'disabled_datastore_properties',
            'disabled_table_properties',
            'incident_contacts',
            'created_at',
            'updated_at',
        )

    def resolve_jdbc_connection(instance, info):
        """Returns JDBC connection information as a separate object.
        """
        return model_to_dict(instance, ['engine', 'host', 'username', 'database', 'port', 'extras'])

    def resolve_ssh_config(instance, info):
        """Returns SSH tunnel settings for the datastore.
        """
        return {
            'is_enabled': instance.ssh_enabled,
            'host': instance.ssh_host,
            'user': instance.ssh_user,
            'port': instance.ssh_port,
            'public_key': info.context.workspace.ssh_public_key,
        }

    def resolve_schemas(instance, info, first=None):
        """Retrieve all of the schemas for a given datastore.
        """
        queryset = instance.schemas.all().order_by('name')
        if first:
            queryset = queryset[:first]
        return queryset

    def resolve_latest_run(instance, info):
        """Retrieve the most recent run for the Schema.
        """
        return instance.last_committed_run

    def resolve_first_run_is_pending(instance, info):
        """Check if the datastore has a completed run.
        """
        return not instance.has_completed_run and not instance.schemas.count()


class DatastoreUserGranteeType(graphene.ObjectType):
    """Represents a group that has limited access to a Datastore.
    """
    id = graphene.ID()

    name = graphene.String()
    type = graphene.String()

    privileges = graphene.List(graphene.String)

    def resolve_id(instance, info):
        """Resolve the GraphQL relay ID
        """
        return shortcuts.to_global_id('UserType', instance['pk'])

    def resolve_type(instance, info):
        """The class type of the object.
        """
        return 'user'

    def resolve_privileges(instance, info):
        return sorted(instance['privileges'])


class DatastoreGroupGranteeType(graphene.ObjectType):
    """Represents a group that has limited access to a Datastore.
    """
    id = graphene.ID()

    name = graphene.String()
    type = graphene.String()

    privileges = graphene.List(graphene.String)

    def resolve_id(instance, info):
        """Resolve the GraphQL relay ID
        """
        return shortcuts.to_global_id('GroupType', instance['pk'])

    def resolve_type(instance, info):
        """The class type of the object.
        """
        return "group"

    def resolve_privileges(instance, info):
        return sorted(instance['privileges'])
