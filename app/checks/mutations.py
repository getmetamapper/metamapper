# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay
from graphene.types.generic import GenericScalar

import app.authorization.permissions as permissions
import app.definitions.permissions as definition_permissions

import app.checks.schema as schema
import app.checks.serializers as serializers

import utils.graphql.scalars as scalars
import utils.mixins.mutations as mixins


class CreateCheck(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Create a data check scoped to a datastore and workspace.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanCreateDatastoreChecks,
    )

    class Input:
        datastore_id = graphene.ID(required=True)
        name = graphene.String(required=True)
        tags = graphene.List(graphene.String, required=False)
        short_desc = graphene.String(required=False)
        interval = graphene.String(required=True)
        query_id = graphene.ID(required=True)
        expectations = graphene.List(schema.CheckExpectation, required=True)

    class Meta:
        serializer_class = serializers.CheckSerializer

    check = graphene.Field(schema.CheckType)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        """We need to grab the datastore before we can process the create request.
        """
        datastore = cls.get_content_object(info, data.pop('datastore_id'))
        arguments = {
            'instance': None,
            'data': data,
            'context': {'datastore': datastore, 'request': info.context},
        }
        return arguments

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(
            creator=info.context.user,
            workspace=info.context.workspace,
        )

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'check': instance,
            'errors': errors,
        }
        return cls(**return_kwargs)


class UpdateCheck(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update data check metadata.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanManageDatastoreChecks,
    )

    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        tags = graphene.List(graphene.String, required=False)
        is_enabled = graphene.Boolean(required=False)
        short_desc = graphene.String(required=False)
        interval = graphene.String(required=False)
        query_id = graphene.ID(required=False)

    class Meta:
        serializer_class = serializers.CheckSerializer

    check = graphene.Field(schema.CheckType)

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'check': instance,
            'errors': errors,
        }
        return cls(**return_kwargs)


class DeleteCheck(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Delete data check and associated objects.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanManageDatastoreChecks,
    )

    class Meta:
        serializer_class = serializers.CheckSerializer


class PreviewCheckQuery(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Upsert a new query object associated with a check.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanManageDatastoreChecks,
    )

    class Input:
        id = graphene.ID(required=True)
        interval = graphene.String(required=True)
        sql_text = graphene.String(required=True)

    class Meta:
        serializer_class = serializers.CheckQuerySerializer

    query = graphene.Field(schema.CheckQueryType)
    query_results = graphene.List(GenericScalar)
    sql_exception = graphene.String()

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        return {
            'instance': None,
            'data': {
                'sql_text': data['sql_text'],
                'interval': data['interval'],
            },
            'context': {
                'datastore': cls.get_content_object(info, data['id']),
                'request': info.context,
            },
        }

    @classmethod
    def perform_mutate(cls, serializer, info, **data):
        catchable_errors = serializer.get_catchable_errors()
        try:
            info.context.dataframe = serializer.get_dataframe()
        except catchable_errors as e:
            return cls(query=None, query_results=None, sql_exception=str(e))
        except Exception:
            return cls(query=None, query_results=None, sql_exception='An unexpected error has occurred.')

        instance, errors = (
            super().perform_mutate(serializer, info, **data)
        )

        return cls(
            query=instance,
            query_results=info.context.dataframe.to_dict(orient='records'),
            errors=errors,
        )

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return instance, errors

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(
            columns=info.context.dataframe.columns.tolist(),
            workspace=info.context.workspace,
        )


class PreviewCheckExpectation(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Preview a new expectation for an existing check.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
    )

    class Input:
        handler_class = graphene.String(required=True)
        handler_input = scalars.JSONObject(required=True)
        pass_value_class = graphene.String(required=True)
        pass_value_input = scalars.JSONObject(required=True)

    class Meta:
        serializer_class = serializers.CheckExpectationSerializer

    expectation = graphene.Field(schema.CheckExpectationType)

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.initialize(workspace=info.context.workspace)

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'expectation': instance,
            'errors': errors,
        }
        return cls(**return_kwargs)


class CreateCheckExpectation(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Create a new expectation for an existing check.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanManageDatastoreChecks,
    )

    class Input:
        id = graphene.ID(required=True)
        handler_class = graphene.String(required=True)
        handler_input = scalars.JSONObject(required=True)
        pass_value_class = graphene.String(required=True)
        pass_value_input = scalars.JSONObject(required=True)

    class Meta:
        serializer_class = serializers.CheckExpectationSerializer

    expectation = graphene.Field(schema.CheckExpectationType)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        """Grab the check and attach it to the serializer context.
        """
        check = cls.get_content_object(info, data.pop('id'))
        return {
            'instance': None,
            'data': data,
            'context': {'check': check, 'request': info.context},
        }

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(workspace=info.context.workspace)

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'expectation': instance,
            'errors': errors,
        }
        return cls(**return_kwargs)


class DeleteCheckExpectation(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Remove an existing expectation from a check.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanManageDatastoreChecks,
    )

    class Meta:
        serializer_class = serializers.CheckExpectationSerializer


class CreateCheckAlertRule(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Create an alert rule associated with a check.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanManageDatastoreChecks,
    )

    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        channel = graphene.String(required=True)
        channel_config = scalars.JSONObject(required=True)
        interval = graphene.String(required=True)

    class Meta:
        serializer_class = serializers.CheckAlertRuleSerializer

    alert_rule = graphene.Field(schema.CheckAlertRuleType)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        """Grab the check and attach it to the serializer context.
        """
        check = cls.get_content_object(info, data.pop('id'))
        return {
            'instance': None,
            'data': data,
            'context': {'check': check, 'request': info.context},
        }

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(workspace=info.context.workspace)

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'alert_rule': instance,
            'errors': errors,
        }
        return cls(**return_kwargs)


class UpdateCheckAlertRule(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update an alert rule associated with a check.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanManageDatastoreChecks,
    )

    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        interval = graphene.String(required=False)
        channel_config = scalars.JSONObject(required=False)

    class Meta:
        serializer_class = serializers.CheckAlertRuleSerializer

    alert_rule = graphene.Field(schema.CheckAlertRuleType)

    @classmethod
    def prepare_response(cls, instance, errors, **data):
        return_kwargs = {
            'alert_rule': instance,
            'errors': errors,
        }
        return cls(**return_kwargs)


class DeleteCheckAlertRule(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Delete an alert rule associated with a check.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanManageDatastoreChecks,
    )

    class Meta:
        serializer_class = serializers.CheckAlertRuleSerializer


class Mutation(graphene.ObjectType):
    """Mutations related to the checks models.
    """
    create_check = CreateCheck.Field()
    update_check = UpdateCheck.Field()
    delete_check = DeleteCheck.Field()

    preview_check_query = PreviewCheckQuery.Field()
    preview_check_expectation = PreviewCheckExpectation.Field()

    create_check_expectation = CreateCheckExpectation.Field()
    delete_check_expectation = DeleteCheckExpectation.Field()

    create_check_alert_rule = CreateCheckAlertRule.Field()
    update_check_alert_rule = UpdateCheckAlertRule.Field()
    delete_check_alert_rule = DeleteCheckAlertRule.Field()
