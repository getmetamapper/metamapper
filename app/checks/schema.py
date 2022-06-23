# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.checks.models as models

import utils.connections as connections
import utils.shortcuts as shortcuts
import utils.graphql.scalars as scalars

from graphene_django import DjangoObjectType
from graphene.types.generic import GenericScalar

from app.authorization.mixins import AuthNode
from app.authorization.permissions import WorkspaceTeamMembersOnly
from app.checks.tasks.context import CheckContext


class CheckExpectation(graphene.InputObjectType):
    """Input type for CheckExpectation model.
    """
    handler_class = graphene.String(required=True)
    handler_input = scalars.JSONObject(required=True)

    pass_value_class = graphene.String(required=True)
    pass_value_input = scalars.JSONObject(required=True)


class CheckConfigurationFieldType(graphene.ObjectType):
    """GraphQL representation of the fields on a dynamic option class.
    """
    label = graphene.String()
    name = graphene.String()
    type = graphene.String()
    options = GenericScalar()
    help_text = graphene.String()
    is_required = graphene.Boolean()


class CheckConfigurationType(graphene.ObjectType):
    """GraphQL representation of an dynamic option class.
    """
    name = graphene.String()
    info = graphene.String()

    handler = graphene.String()
    details = graphene.List(CheckConfigurationFieldType)


class CheckIntervalType(graphene.ObjectType):
    """GraphQL representation of a Check interval.
    """
    label = graphene.String()
    value = graphene.String()

    def resolve_label(value, info):
        return shortcuts.humanize_timedelta(value)

    def resolve_value(value, info):
        return value


class CheckAlertChannelType(graphene.ObjectType):
    """GraphQL representation of a Check alert rule channel type.
    """
    label = graphene.String()
    value = graphene.String()


class CheckType(AuthNode, DjangoObjectType):
    """GraphQL representation of a Check.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    interval = graphene.Field(CheckIntervalType)

    class Meta:
        model = models.Check
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        exclude_fields = []

    @classmethod
    def get_node(cls, info, id):
        """We should only return checks related to the current workspace.
        """
        return models.Check.objects.filter(
            workspace=info.context.workspace,
            id=id,
        ).first()

    def resolve_schedule_interval(instance, info):
        """str: Humanized version of interval.
        """
        return instance.interval


class CheckQueryType(AuthNode, DjangoObjectType):
    """GraphQL representation of a CheckQuery.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    class Meta:
        model = models.CheckQuery
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        only_fields = ('id', 'key', 'columns', 'sql_text',)

    @classmethod
    def get_node(cls, info, id):
        return models.CheckQuery.objects.filter(
            workspace=info.context.workspace,
            id=id,
        ).first()


class CheckExpectationType(AuthNode, DjangoObjectType):
    """GraphQL representation of a CheckExpectation.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    description = graphene.String()
    handler_input = GenericScalar()
    pass_value_input = GenericScalar()

    class Meta:
        model = models.CheckExpectation
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        exclude_fields = []

    @classmethod
    def get_node(cls, info, id):
        return models.CheckExpectation.objects.filter(
            workspace=info.context.workspace,
            id=id,
        ).first()


class CheckExpectationResultType(AuthNode, DjangoObjectType):
    """GraphQL representation of a CheckExpectationResult.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    expectation = graphene.Field(CheckExpectationType)

    class Meta:
        model = models.CheckExpectationResult
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        only_fields = (
            'expectation',
            'epoch',
            'passed',
            'observed_value',
            'expected_value',)


class CheckExecutionType(AuthNode, DjangoObjectType):
    """GraphQL representation of a CheckExecution.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    status = graphene.String()
    executed_query_text = graphene.String()
    expectation_results = graphene.List(CheckExpectationResultType)

    class Meta:
        model = models.CheckExecution
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        exclude_fields = ['query']

    @classmethod
    def get_node(cls, info, id):
        return models.CheckExecution.objects.filter(
            workspace=info.context.workspace,
            id=id,
        ).first()

    def resolve_expectation_results(instance, info):
        """Results for each expectation for this execution.
        """
        return instance.expectation_results.order_by('epoch')

    def resolve_executed_query_text(instance, info):
        """The actual query that was executed against the datastore.
        """
        context = CheckContext(instance.epoch, instance.job.interval)
        template = instance.query.to_template()
        return template.render(**context.to_dict())


class CheckAlertRuleType(AuthNode, DjangoObjectType):
    """GraphQL representation of a CheckAlertRule.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    pk = graphene.String()

    interval = graphene.Field(CheckIntervalType)

    channel = graphene.String()
    channel_config = GenericScalar()

    class Meta:
        model = models.CheckAlertRule
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        exclude_fields = []

    def resolve_pk(instance, info):
        return instance.id
