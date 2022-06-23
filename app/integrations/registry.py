# -*- coding: utf-8 -*-
from collections import namedtuple

from app.integrations.pagerduty.integration import PagerDutyIntegration
from app.integrations.slack.integration import SlackIntegration


Integration = namedtuple('Integration', ['id', 'name', 'handler'])


AVAILABLE_INTEGRATIONS = [
    Integration('PAGERDUTY', 'PagerDuty', PagerDutyIntegration),
    Integration('SLACK', 'Slack', SlackIntegration),
]


def get_available_integrations(workspace):
    """Retrieve the available integrations related to the workspace.
    """
    installed = workspace.integrations.values_list('integration', flat=True).distinct('integration')
    resultset = []
    for integration_id, integration_name, handler in AVAILABLE_INTEGRATIONS:
        resultset.append({
            'handler': integration_id,
            'name': integration_name,
            'installed': integration_id in installed,
            'tags': handler.tags,
        })
    return resultset


def find_integration(integration_id):
    """Retrieve integration by ID.
    """
    return next(filter(lambda i: i.id == integration_id, AVAILABLE_INTEGRATIONS), None)


def get_integration(workspace, integration_id):
    """Retrieve the available integrations related to the workspace.
    """
    integration = find_integration(integration_id)

    if not integration:
        return None

    handler_fields = integration.handler.get_fields()
    handler_kwargs = {
        'name': integration.name,
        'info': None,
        'handler': integration.id,
        'installed': workspace.integration_installed(integration.id),
        'tags': integration.handler.tags,
        'details': [
            {
                'name': name,
                'type': field.__class__.__name__,
                'label': field.label,
                'options': field.get_options(),
                'help_text': field.help_text,
                'is_display': name == integration.handler.Meta.displayable_key,
                'is_required': field.required,
            }
            for name, field in handler_fields
        ],
    }

    return handler_kwargs
