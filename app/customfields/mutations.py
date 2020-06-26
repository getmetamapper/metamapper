# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.authorization.permissions as permissions
import app.customfields.models as models
import app.customfields.scalars as scalars
import app.customfields.schema as schema
import app.customfields.serializers as serializers

import utils.mixins.mutations as mixins
import utils.errors as errors
import utils.graphql.scalars as utils_scalars


class CreateCustomField(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Create a custom field instance.
    """
    permission_classes = (permissions.WorkspaceWriteAccessOnly,)

    class Input:
        field_name = graphene.String(required=True)
        field_type = graphene.String(required=True)
        validators = utils_scalars.JSONObject(required=True)
        short_desc = graphene.String(required=False)
        content_type = graphene.String(required=True)

    class Meta:
        serializer_class = serializers.CustomFieldSerializer

    custom_field = graphene.Field(schema.CustomFieldType)

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(workspace=info.context.workspace)

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'custom_field': instance,
            'errors': errors,
        }
        return cls(**return_kwargs)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        """Retrieve appropriate objects for the transaction.
        """
        content_type = models.CustomField.get_content_type_from_name(data["content_type"])
        return {
            "instance": None,
            "data": {
                "field_name": data["field_name"],
                "field_type": data["field_type"],
                "validators": data["validators"],
                "short_desc": data.get("short_desc"),
                "content_type": content_type,
            },
            "context": {
                "request": info.context,
            },
        }


class UpdateCustomField(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Change a custom field instance.
    """
    permission_classes = (permissions.WorkspaceWriteAccessOnly,)

    class Input:
        id = graphene.ID(required=True)
        field_name = graphene.String(required=False)
        validators = utils_scalars.JSONObject(required=False)
        short_desc = graphene.String(required=False)

    class Meta:
        serializer_class = serializers.CustomFieldSerializer

    custom_field = graphene.Field(schema.CustomFieldType)

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'custom_field': instance,
            'errors': errors,
        }
        return cls(**return_kwargs)


class DeleteCustomField(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Remove a custom field instance.
    """
    permission_classes = (permissions.WorkspaceWriteAccessOnly,)

    class Input:
        id = graphene.ID(required=True)

    class Meta:
        serializer_class = serializers.CustomFieldSerializer


class UpdateCustomProperties(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update multiple custom fields for a model instance.
    """
    permission_classes = (permissions.WorkspaceWriteAccessOnly,)

    class Input:
        object_id = graphene.ID(required=True)
        properties = graphene.List(utils_scalars.JSONObject, required=True)

    class Meta:
        serializer_class = serializers.CustomPropertiesSerializer
        lookup_field = 'object_id'

    custom_properties = graphene.Field(scalars.CustomPropScalar)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        """Transform input into serializer format.
        """
        instance = cls.get_instance(info, data)

        if not instance:
            raise errors.PermissionDeniedError()

        properties = {
            p['id']: p['value']
            for p in data['properties'] if 'id' in p
        }

        return {
            "instance": instance,
            "data": {
                "properties": properties,
            },
            "partial": True,
            "context": {
                "request": info.context,
            },
        }

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'custom_properties': instance,
            'errors': errors,
        }
        return cls(**return_kwargs)


class Mutation(graphene.ObjectType):
    """Mutations related to the customfields models.
    """
    create_custom_field = CreateCustomField.Field()
    update_custom_field = UpdateCustomField.Field()
    delete_custom_field = DeleteCustomField.Field()

    update_custom_properties = UpdateCustomProperties.Field()
