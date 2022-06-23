# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.factories as factories

import app.integrations.registry as registry


class GetAvailableIntegrationTests(cases.TestCase):
    """Test cases for the `get_available_integrations` function.
    """
    def setUp(self):
        self.workspace = factories.WorkspaceFactory()

    def test_get_available_integrations(self):
        integrations = registry.get_available_integrations(self.workspace)

        self.assertEqual(len(integrations), len(registry.AVAILABLE_INTEGRATIONS))
        self.assertEqual(integrations[0], {
            'handler': 'PAGERDUTY',
            'name': 'PagerDuty',
            'installed': False,
            'tags': ['Alerting'],
        })


class FindIntegrationTests(cases.TestCase):
    """Test cases for the `find_integration` function.
    """
    def test_find_integration_exists(self):
        integration = registry.find_integration('PAGERDUTY')

        self.assertEqual(integration.id, 'PAGERDUTY')
        self.assertEqual(integration.name, 'PagerDuty')
        self.assertEqual(integration.handler, registry.PagerDutyIntegration)

    def test_find_integration_not_exists(self):
        self.assertIsNone(registry.find_integration('NOTHING'))
