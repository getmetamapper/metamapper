# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.authorization.permissions as permissions
import app.definitions.permissions as definition_permissions

import app.definitions.models as models
import app.definitions.tasks as tasks
import app.definitions.schema as schema
import app.definitions.serializers as serializers
import app.audit.tasks as audit
import app.omnisearch.tasks as omnisearch

import utils.graphql.scalars as utils_scalars
import utils.errors as errors
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
        extras = utils_scalars.JSONObject(required=False)

        ssh_enabled = graphene.Boolean(required=False, default_value=False)
        ssh_host = graphene.String(required=False)
        ssh_user = graphene.String(required=False)
        ssh_port = graphene.Int(required=False)

    class Meta:
        serializer_class = serializers.DatastoreSerializer

    datastore = graphene.Field(schema.DatastoreType)

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(
            creator=info.context.user,
            workspace=info.context.workspace,
        )


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
        extras = utils_scalars.JSONObject(required=False)

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
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            "ok": (errors is None),
            "errors": errors,
        }
        return cls(**return_kwargs)


class UpdateDatastoreMetadata(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update an existing datastore.
    """
    nullable_fields = ["short_desc"]

    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanUpdateDatastoreSettings,
    )

    class Input:
        id = graphene.ID(required=True)

        is_enabled = graphene.Boolean(required=False)
        short_desc = graphene.String(required=False)

        name = graphene.String(required=False)
        tags = graphene.List(graphene.String, required=False)
        interval = graphene.String(required=False)
        incident_contacts = graphene.List(graphene.String, required=False)

    class Meta:
        serializer_class = serializers.DatastoreSerializer

    datastore = graphene.Field(schema.DatastoreType)


class DisableDatastoreCustomFields(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update the disabled custom fields on a datastore.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanUpdateDatastoreSettings,
    )

    class Input:
        id = graphene.ID(required=True)

        disabled_datastore_properties = graphene.List(graphene.String, required=False)
        disabled_table_properties = graphene.List(graphene.String, required=False)

    class Meta:
        serializer_class = serializers.DisableCustomFieldsSerializer

    datastore = graphene.Field(schema.DatastoreType)


class UpdateDatastoreJdbcConnection(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update an existing datastore.
    """
    nullable_fields = ["ssh_host", "ssh_user", "ssh_port"]

    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanUpdateDatastoreConnection,
    )

    class Input:
        id = graphene.ID(required=True)

        username = graphene.String(required=False)
        password = graphene.String(required=False)
        database = graphene.String(required=False)
        host = graphene.String(required=False)
        port = graphene.Int(required=False)
        extras = utils_scalars.JSONObject(required=False)

        ssh_enabled = graphene.Boolean(required=False)
        ssh_host = graphene.String(required=False)
        ssh_user = graphene.String(required=False)
        ssh_port = graphene.Int(required=False)

    class Meta:
        serializer_class = serializers.DatastoreSerializer

    datastore = graphene.Field(schema.DatastoreType)


class ToggleDatastoreObjectPermissions(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update an existing datastore.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanUpdateDatastoreAccess,
    )

    class Input:
        id = graphene.ID(required=True)

    class Meta:
        serializer_class = serializers.ToggleDatastoreObjectPermissionsSerializer

    is_enabled = graphene.Boolean()

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            "is_enabled": instance.object_permissions_enabled,
            "errors": errors,
        }
        return cls(**return_kwargs)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        """Retrieve appropriate objects for the transaction.
        """
        instance = cls.get_instance(info, data)

        if not instance:
            raise errors.PermissionDenied()

        return {
            "instance": instance,
            "data": {
                "object_permissions_enabled": not instance.object_permissions_enabled,
            },
            "context": {
                "request": info.context,
            },
        }


class UpdateDatastoreAccessPrivileges(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update the permissions for a datastore and users/groups.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanUpdateDatastoreAccess,
    )

    class Input:
        id = graphene.ID(required=True)
        object_id = graphene.ID(required=True)
        privileges = graphene.List(graphene.String, required=True)

    class Meta:
        serializer_class = serializers.DatastoreAccessPrivilegesSerializer

    ok = graphene.Boolean()

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            "ok": (errors is None),
            "errors": errors,
        }
        return cls(**return_kwargs)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        """Retrieve appropriate objects for the transaction.
        """
        instance = cls.get_instance(info, data)

        if not instance or not instance.object_permissions_enabled:
            raise errors.PermissionDenied()

        return {
            "instance": instance,
            "data": {
                "content_object": cls.get_content_object(info, data["object_id"]),
                "privileges": data["privileges"],
            },
            "context": {
                "request": info.context,
            },
        }


class DeleteDatastore(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Permanently remove an existing datastore.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanDeleteDatastore,
    )

    class Meta:
        serializer_class = serializers.DatastoreSerializer

    @classmethod
    def tasks_on_success(cls, instance, info):
        """We should queue this datastore to be hard-deleted.
        """
        return [
            {
                "function": tasks.hard_delete_datastore.delay,
                "arguments": {
                    "datastore_id": instance.id,
                },
            }
        ]


class UpdateTableMetadata(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update editable fields on a table.
    """
    nullable_fields = ["short_desc", "readme"]

    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanUpdateDatastoreMetadata,
    )

    class Input:
        id = graphene.ID(required=True)
        tags = graphene.List(graphene.String, required=False)
        readme = graphene.String(required=False)
        short_desc = graphene.String(required=False)

    class Meta:
        serializer_class = serializers.TableSerializer

    table = graphene.Field(schema.TableType)

    @classmethod
    def tasks_on_success(cls, instance, info):
        """We should re-index the object in Elasticsearch immediately.
        """
        return [
            {
                "function": omnisearch.update_single_es_object.delay,
                "arguments": {
                    "index_name": "table",
                    "instance_id": instance.id,
                },
            }
        ]


class UpdateColumnMetadata(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update editable fields on a column.
    """
    nullable_fields = ["short_desc", "readme"]

    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanUpdateDatastoreMetadata,
    )

    class Input:
        id = graphene.ID(required=True)
        readme = graphene.String(required=False)
        short_desc = graphene.String(required=False)

    class Meta:
        serializer_class = serializers.ColumnSerializer

    column = graphene.Field(schema.ColumnType)

    @classmethod
    def tasks_on_success(cls, instance, info):
        """We should re-index the object in Elasticsearch immediately.
        """
        return [
            {
                "function": omnisearch.update_single_es_object.delay,
                "arguments": {
                    "index_name": "column",
                    "instance_id": instance.id,
                },
            }
        ]


class CreateAssetOwner(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Create an owner for the provided data asset.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanCreateAssetOwner,
    )

    class Input:
        object_id = graphene.ID(required=True)
        owner_id = graphene.ID(required=True)
        classification = graphene.String(required=True, default_value=models.AssetOwner.BUSINESS)
        order = graphene.Int(required=False)

    class Meta:
        serializer_class = serializers.AssetOwnerSerializer

    assetowner = graphene.Field(schema.AssetOwnerType, name="assetOwner")

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(workspace=info.context.workspace)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        """Retrieve appropriate objects for the transaction.
        """
        return {
            "instance": None,
            "data": {
                "classification": data["classification"],
                "content_object": cls.get_content_object(info, data["object_id"]),
                "order": data["order"],
                "owner": cls.get_content_object(info, data["owner_id"]),
            },
            "context": {
                "request": info.context,
            },
        }


class UpdateAssetOwner(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update an owner for the provided data asset.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanUpdateDatastoreMetadata,
    )

    class Input:
        id = graphene.ID(required=True)
        order = graphene.Int(required=True)

    class Meta:
        serializer_class = serializers.AssetOwnerSerializer

    assetowner = graphene.Field(schema.AssetOwnerType, name="assetOwner")


class DeleteAssetOwner(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Remove an owner for the provided data asset.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanUpdateDatastoreMetadata,
    )

    class Meta:
        serializer_class = serializers.AssetOwnerSerializer

    @classmethod
    def tasks_on_success(cls, instance, info):
        """List of tasks to dispatch.
        """
        arguments = {
            "actor_id": info.context.user.id,
            "workspace_id": info.context.workspace.id,
            "verb": "removed an owner from",
            "old_values": {},
            "new_values": {},
        }
        arguments.update(serializers.get_asset_owner_audit_kwargs(instance))
        return [
            {
                "function": audit.audit.delay,
                "arguments": arguments,
            }
        ]


class Mutation(graphene.ObjectType):
    """Mutations for managing definitions.
    """
    create_datastore = CreateDatastore.Field()
    delete_datastore = DeleteDatastore.Field()

    update_datastore_metadata = UpdateDatastoreMetadata.Field()
    update_datastore_jdbc_connection = UpdateDatastoreJdbcConnection.Field()
    update_datastore_access_privileges = UpdateDatastoreAccessPrivileges.Field()

    toggle_datastore_object_permissions = ToggleDatastoreObjectPermissions.Field()

    disable_datastore_custom_fields = DisableDatastoreCustomFields.Field()

    test_jdbc_connection = TestJdbcConnection.Field()

    update_table_metadata = UpdateTableMetadata.Field()
    update_column_metadata = UpdateColumnMetadata.Field()

    create_asset_owner = CreateAssetOwner.Field()
    update_asset_owner = UpdateAssetOwner.Field()
    delete_asset_owner = DeleteAssetOwner.Field()
