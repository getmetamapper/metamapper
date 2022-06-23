# -*- coding: utf-8 -*-
import abc
import rest_framework.serializers as serializers
import utils.shortcuts as shortcuts

from django.apps import apps
from django.conf import settings


class Alert(abc.ABC):
    """Base class for alert delivery.
    """
    class Meta:
        name = None
        integration = None
        validator = None

    def __init__(self, alert_rule, check, check_execution, check_error):
        self.alert_rule = alert_rule
        self.check = check
        self.check_execution = check_execution
        self.check_error = check_error
        self.datastore = check.datastore
        self.workspace = check.workspace

    @property
    def check_name(self):
        return self.check.name

    @property
    def check_timestamp(self):
        return self.check.created_at.strftime('%Y-%m-%dT%H:%M:%S')

    @property
    def check_url(self):
        parts = [
            settings.WEBSERVER_ORIGIN,
            '/',
            self.workspace.slug,
            '/datastores/',
            self.datastore.slug,
            '/checks/',
            self.check.id,
            '?selectedExecution=',
            self.selected_execution,
        ]
        return "".join(parts)

    @property
    def selected_execution(self):
        return shortcuts.to_global_id('CheckExecutionType', self.check_execution.id)

    @property
    def recipient_emails(self):
        """list<str>: Emails to deliver notification to.
        """
        return self.alert_rule.channel_config.get('emails', [])

    @classmethod
    def get_fields(cls):
        d = {}
        for k, v in cls.Meta.validator().fields.items():
            if isinstance(v, serializers.Field):
                d[k] = v
        return [(k, v) for k, v in d.items()]

    def meets_criteria(self):
        """bool: Does the scenario match the requirements on the alert rule?
        """
        return True

    def deliver(self):
        """void: Queue alerts.
        """
        if not self.meets_criteria():
            return

        self.send()

    @abc.abstractmethod
    def send(self):
        pass


class Validator(serializers.Serializer):
    """Base class for alert attribute validator.
    """
    def validate_integration_id(self, integration_id):
        """Confirm that the integration exists and is related to the current workspace.
        """
        integration_class = apps.get_model('integrations.IntegrationConfig')
        integration_kwargs = {
            'id': integration_id,
            'workspace': self.context['request'].workspace,
        }
        if not integration_class.objects.filter(**integration_kwargs).exists():
            raise serializers.ValidationError('Integration could not be found.')
        return integration_id
