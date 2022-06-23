# -*- coding: utf-8 -*-
import graphene

import app.definitions.permissions as permissions

import utils.errors as errors
import utils.shortcuts as shortcuts

import app.checks.alerts as alerts
import app.checks.schema as schema
import app.checks.models as models
import app.checks.tasks.expectations as expectations
import app.checks.tasks.pass_values as pass_values

from app.authorization.fields import AuthConnectionField
from app.authorization import permissions as auth_perms
from app.definitions.models import Datastore


class Query(graphene.ObjectType):
    """Queries related to the checks models.
    """
    check_interval_options = graphene.List(schema.CheckIntervalType)

    check_expectation_handlers = graphene.List(schema.CheckConfigurationType)

    check_pass_value_handlers = graphene.List(schema.CheckConfigurationType)

    check_alert_channels = graphene.List(schema.CheckConfigurationType)

    check = graphene.Field(schema.CheckType, id=graphene.ID(required=True))
    checks = AuthConnectionField(
        type=schema.CheckType,
        datastore_id=graphene.ID(required=True),
    )

    check_expectations = AuthConnectionField(
        type=schema.CheckExpectationType,
        check_id=graphene.ID(required=True),
    )

    check_alert_rule = graphene.Field(schema.CheckAlertRuleType, id=graphene.ID(required=True))
    check_alert_rules = AuthConnectionField(
        type=schema.CheckAlertRuleType,
        check_id=graphene.ID(required=True),
    )

    check_execution = graphene.Field(schema.CheckExecutionType, id=graphene.ID(required=True))
    check_executions = AuthConnectionField(
        type=schema.CheckExecutionType,
        check_id=graphene.ID(required=True),
    )

    @auth_perms.login_required
    def resolve_check_interval_options(self, info):
        """Retrieve the check interval options.
        """
        return models.Check.INTERVAL_CHOICES

    @auth_perms.login_required
    def resolve_check_expectation_handlers(self, info):
        """Retrieve the check expectation handlers.
        """
        return expectations.get_handler_configuration_options()

    @auth_perms.login_required
    def resolve_check_pass_value_handlers(self, info):
        """Retrieve the check pass value handlers.
        """
        return pass_values.get_handler_configuration_options()

    @auth_perms.login_required
    def resolve_check_alert_channels(self, info):
        """Retrieve available alert channels.
        """
        return alerts.get_alert_configuration_options(info.context.workspace)

    @permissions.can_view_datastore_objects(lambda instance: instance.datastore)
    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_check(self, info, id):
        """Retrieve a single check by ID.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(id, True),
        }
        return shortcuts.get_object_or_404(models.Check, **get_kwargs)

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_checks(self, info, datastore_id, *args, **kwargs):
        """Retrieve a list of checks associated with a datastore.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(datastore_id, True),
        }

        datastore = shortcuts.get_object_or_404(Datastore, **get_kwargs)

        if not permissions.request_can_view_datastore(info, datastore):
            raise errors.PermissionDenied()

        return datastore.checks.prefetch_related('creator').order_by('-created_at')

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_check_expectations(self, info, check_id, *args, **kwargs):
        """Retrieve check expectations associated with a check.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(check_id, True),
        }

        check = shortcuts.get_object_or_404(models.Check, **get_kwargs)

        if not permissions.request_can_view_datastore(info, check.datastore):
            raise errors.PermissionDenied()

        return check.expectations.order_by('created_at')

    @permissions.can_view_datastore_objects(lambda instance: instance.job.datastore)
    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_check_alert_rule(self, info, id):
        """Retrieve a check alert rule based on the provided ID.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(id, True),
        }
        return shortcuts.get_object_or_404(models.CheckAlertRule, **get_kwargs)

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_check_alert_rules(self, info, check_id, *args, **kwargs):
        """Retrieve alert rules related to a check.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(check_id, True),
        }

        check = shortcuts.get_object_or_404(models.Check, **get_kwargs)

        if not permissions.request_can_view_datastore(info, check.datastore):
            raise errors.PermissionDenied()

        return check.alert_rules.prefetch_related('last_failure').order_by('created_at')

    @permissions.can_view_datastore_objects(lambda instance: instance.job.datastore)
    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_check_execution(self, info, id):
        """Retrieve a check execution based on the provided ID.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(id, True),
        }
        return shortcuts.get_object_or_404(models.CheckExecution, **get_kwargs)

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_check_executions(self, info, check_id, *args, **kwargs):
        """Retrieve check executions associated with a check check.
        """
        get_kwargs = {
            'workspace': info.context.workspace,
            'pk': shortcuts.from_global_id(check_id, True),
        }

        check = shortcuts.get_object_or_404(models.Check, **get_kwargs)

        if not permissions.request_can_view_datastore(info, check.datastore):
            raise errors.PermissionDenied()

        return check.executions.filter(started_at__isnull=False).order_by('-created_at')
