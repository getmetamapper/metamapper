# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.authorization.permissions as permissions

import app.definitions.schema as schema
import app.definitions.serializers as serializers

import utils.mixins.mutations as mixins


class CreateDatastore(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Create a datastore scoped to a workspace.
    """
    permission_classes = (permissions.WorkspaceWriteAccessOnly,)

    class Input:
        name = graphene.String(required=True)
        tags = graphene.List(graphene.String, required=False)

        engine = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        database = graphene.String(required=True)
        host = graphene.String(required=True)
        port = graphene.Int(required=True)

        ssh_enabled = graphene.Boolean(required=False, default_value=False)
        ssh_host = graphene.String(required=False)
        ssh_user = graphene.String(required=False)
        ssh_port = graphene.Int(required=False)

    class Meta:
        serializer_class = serializers.DatastoreSerializer

    datastore = graphene.Field(schema.DatastoreType)

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(workspace=info.context.workspace)


class TestJdbcConnection(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Check if provided JDBC connection is valid.
    """
    permission_classes = (permissions.WorkspaceWriteAccessOnly,)

    class Input:
        engine = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        database = graphene.String(required=True)
        host = graphene.String(required=True)
        port = graphene.Int(required=True)

        ssh_enabled = graphene.Boolean(required=False, default_value=False)
        ssh_host = graphene.String(required=False)
        ssh_user = graphene.String(required=False)
        ssh_port = graphene.Int(required=False)

    class Meta:
        serializer_class = serializers.JdbcConnectionSerializer

    ok = graphene.Boolean()

    @classmethod
    def perform_save(cls, serializer, info):
        return None

    @classmethod
    def prepare_response(cls, instance, errors):
        return_kwargs = {
            'ok': (errors is None),
            'errors': errors,
        }
        return cls(**return_kwargs)


class UpdateDatastoreMetadata(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update an existing datastore.
    """
    nullable_fields = ['short_desc']

    permission_classes = (permissions.WorkspaceWriteAccessOnly,)

    class Input:
        id = graphene.ID(required=True)

        is_enabled = graphene.Boolean(required=False)
        short_desc = graphene.String(required=False)
        name = graphene.String(required=False)
        tags = graphene.List(graphene.String, required=False)

    class Meta:
        serializer_class = serializers.DatastoreSerializer

    datastore = graphene.Field(schema.DatastoreType)


class UpdateDatastoreJdbcConnection(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update an existing datastore.
    """
    nullable_fields = ['ssh_host', 'ssh_user', 'ssh_port']

    permission_classes = (permissions.WorkspaceWriteAccessOnly,)

    class Input:
        id = graphene.ID(required=True)

        username = graphene.String(required=False)
        password = graphene.String(required=False)
        database = graphene.String(required=False)
        host = graphene.String(required=False)
        port = graphene.Int(required=False)

        ssh_enabled = graphene.Boolean(required=False)
        ssh_host = graphene.String(required=False)
        ssh_user = graphene.String(required=False)
        ssh_port = graphene.Int(required=False)

    class Meta:
        serializer_class = serializers.DatastoreSerializer

    datastore = graphene.Field(schema.DatastoreType)


class DeleteDatastore(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Permanently remove an existing datastore.
    """
    permission_classes = (permissions.WorkspaceWriteAccessOnly,)

    class Meta:
        serializer_class = serializers.DatastoreSerializer


class UpdateTableMetadata(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update editable fields on a table.
    """
    nullable_fields = ['short_desc']

    permission_classes = (permissions.WorkspaceWriteAccessOnly,)

    class Input:
        id = graphene.ID(required=True)
        tags = graphene.List(graphene.String, required=False)
        short_desc = graphene.String(required=False)

    class Meta:
        serializer_class = serializers.TableSerializer

    table = graphene.Field(schema.TableType)


class UpdateColumnMetadata(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update editable fields on a column.
    """
    nullable_fields = ['short_desc']

    permission_classes = (permissions.WorkspaceWriteAccessOnly,)

    class Input:
        id = graphene.ID(required=True)
        short_desc = graphene.String(required=False)

    class Meta:
        serializer_class = serializers.ColumnSerializer

    column = graphene.Field(schema.ColumnType)


class Mutation(graphene.ObjectType):
    """Mutations for managing definitions.
    """
    create_datastore = CreateDatastore.Field()
    delete_datastore = DeleteDatastore.Field()

    update_datastore_metadata = UpdateDatastoreMetadata.Field()
    update_datastore_jdbc_connection = UpdateDatastoreJdbcConnection.Field()
    test_jdbc_connection = TestJdbcConnection.Field()

    update_table_metadata = UpdateTableMetadata.Field()
    update_column_metadata = UpdateColumnMetadata.Field()
