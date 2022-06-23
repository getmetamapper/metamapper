# -*- coding: utf-8 -*-
from utils.shortcuts import load_class

from app.checks.alerts.email import EmailAlert
from app.checks.alerts.pagerduty import PagerDutyAlert
from app.checks.alerts.slack import SlackAlert


__all__ = ['EmailAlert', 'PagerDutyAlert', 'SlackAlert']


def get_alert_classes(workspace=None):
    """Return the classes for each alert.
    """
    output = []
    for alert_class in __all__:
        alert = load_class(__name__, alert_class)
        if workspace and not workspace.integration_installed(alert.Meta.integration):
            continue
        output.append(alert)
    return output


def get_alert_configuration_options(workspace):
    """Return the configuration options for each alert.
    """
    if workspace is None:
        raise ValueError('Workspace cannot be NULL.')
    output = []
    for alert in get_alert_classes(workspace):
        alert_fields = alert.get_fields()
        alert_kwargs = {
            'name': getattr(alert.Meta, 'name', None),
            'info': None,
            'handler': alert.Meta.integration,
            'details': [
                {
                    'name': name,
                    'type': field.__class__.__name__,
                    'label': field.label,
                    'options': field.get_options(alert.Meta.integration, workspace),
                    'help_text': field.help_text,
                    'is_required': field.required,
                }
                for name, field in alert_fields
            ],
        }
        output.append(alert_kwargs)
    return output
